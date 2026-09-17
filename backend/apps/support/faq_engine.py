"""
CSV-backed FAQ retrieval for the storefront chatbot.

There is deliberately no Django model here. The FAQ list is editorial
content that ships with the codebase and changes by editing a file, not by
any customer action — so a model would buy nothing but a migration and an
admin screen. A CSV means a non-developer can open `data/faqs.csv` in a
spreadsheet, add a row, and the bot answers the new question on the next
message: the loader below re-reads the file whenever its mtime changes, so
no server restart is needed in development either.

Matching is stdlib-only (no scikit-learn, no embeddings, nothing to pip
install). The score for a row blends three signals:

  1. IDF-weighted token overlap — the main signal. Weighting by inverse
     document frequency stops words that appear in most rows ("order",
     "product") from dominating the ones that actually discriminate
     ("refund", "vendor", "bkash").
  2. Explicit keyword hits — the `keywords` column lets an editor pin
     phrasings a customer would use that do not appear in the question
     text itself ("cod", "money back", "where is my parcel").
  3. A difflib similarity ratio — a small tie-breaker that keeps typos
     like "payement" or "refnd" from dropping the score to zero.

Results below CONFIDENT_THRESHOLD are returned as suggestions instead of a
confident answer, so the bot says "did you mean..." rather than replying
with a plausible-sounding wrong FAQ.
"""

from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from threading import Lock

FAQ_CSV_PATH = Path(__file__).resolve().parent / "data" / "faqs.csv"

# Above this score we answer directly; between the two we offer suggestions;
# below the low mark we fall back to the "contact support" reply.
CONFIDENT_THRESHOLD = 0.42
SUGGEST_THRESHOLD = 0.14

MAX_QUERY_CHARS = 500
MAX_SUGGESTIONS = 3

# Words carrying no discriminating power for FAQ lookup. Kept short and
# hand-picked rather than importing a stopword corpus.
STOPWORDS = frozenset(
    """
    a an the is are was were be been being am do does did doing done
    i me my mine we us our ours you your yours he she it its they them their
    this that these those there here what which who whom whose when where why how
    can could should would will shall may might must have has had
    of in on at to from for with without by about into over under again
    and or but if then than so as too very just also
    get got give gives please thanks thank hi hello hey ok okay
    want need like know tell help
    """.split()
)

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Light normalisation for the spellings customers actually type.
_SYNONYMS = {
    "cod": "cash on delivery",
    "signin": "sign in",
    "signup": "sign up",
    "login": "log in",
    "logout": "log out",
    "cancelled": "cancel",
    "canceling": "cancel",
    "cancelation": "cancel",
    "delivered": "deliver",
    "delivery": "deliver",
    "shipping": "ship",
    "shipped": "ship",
    "payment": "pay",
    "payments": "pay",
    "paid": "pay",
    "paying": "pay",
    "orders": "order",
    "ordered": "order",
    "ordering": "order",
    "products": "product",
    "items": "item",
    "refunds": "refund",
    "refunded": "refund",
    "returns": "return",
    "returned": "return",
    "vendors": "vendor",
    "sellers": "vendor",
    "seller": "vendor",
    "accounts": "account",
    "passwords": "password",
    "prices": "price",
    "pricing": "price",
    "taka": "bdt",
    "tk": "bdt",
}


def _normalise(text: str) -> str:
    return (text or "").lower().strip()


def _tokenise(text: str) -> list[str]:
    """Lowercase -> expand synonyms -> split to words -> drop stopwords."""
    tokens: list[str] = []
    for raw in _TOKEN_RE.findall(_normalise(text)):
        expanded = _SYNONYMS.get(raw, raw)
        for token in expanded.split():
            if token and token not in STOPWORDS and len(token) > 1:
                tokens.append(token)
    return tokens


@dataclass
class FaqEntry:
    id: str
    category: str
    question: str
    answer: str
    keywords: list[str] = field(default_factory=list)
    question_tokens: set[str] = field(default_factory=set)
    keyword_tokens: set[str] = field(default_factory=set)
    all_tokens: set[str] = field(default_factory=set)

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "question": self.question,
            "answer": self.answer,
        }


class FaqIndex:
    """An in-memory, IDF-weighted index over the FAQ rows."""

    def __init__(self, entries: list[FaqEntry]):
        self.entries = entries
        self.idf = self._build_idf(entries)

    @staticmethod
    def _build_idf(entries: list[FaqEntry]) -> dict[str, float]:
        total = len(entries) or 1
        document_frequency: dict[str, int] = {}
        for entry in entries:
            for token in entry.all_tokens:
                document_frequency[token] = document_frequency.get(token, 0) + 1
        # Smoothed IDF; +1 keeps every weight strictly positive.
        return {
            token: math.log((total + 1) / (count + 1)) + 1.0
            for token, count in document_frequency.items()
        }

    def _score(self, query_tokens: set[str], query_text: str, entry: FaqEntry) -> float:
        # A query made entirely of stopwords ("who are you", "can I?") has no
        # tokens to weigh, but may still hit a keyword phrase verbatim — so
        # zero out the token signals rather than bailing out of scoring.
        query_weight = sum(self.idf.get(token, 1.0) for token in query_tokens)

        if query_weight > 0:
            # 1. IDF-weighted overlap against the question text.
            overlap = query_tokens & entry.question_tokens
            question_score = sum(self.idf.get(token, 1.0) for token in overlap) / query_weight
        else:
            question_score = 0.0

        # 2. Editor-supplied keyword hits, as loose token overlap.
        keyword_score = 0.0
        if entry.keyword_tokens and query_weight > 0:
            keyword_overlap = query_tokens & entry.keyword_tokens
            if keyword_overlap:
                keyword_score = sum(
                    self.idf.get(token, 1.0) for token in keyword_overlap
                ) / query_weight

        # 2b. A whole keyword *phrase* appearing verbatim is a much stronger
        #     signal than its tokens scattered across the query — "money back"
        #     should reach the refund row even though neither word appears in
        #     "How do I request a refund?". Matched on word boundaries so a
        #     short phrase like "cod" cannot fire inside "record", and scaled
        #     by phrase length so longer phrases count for more.
        phrase_bonus = 0.0
        for phrase in entry.keywords:
            if len(phrase) < 3:
                continue
            if re.search(rf"\b{re.escape(phrase)}\b", query_text):
                phrase_bonus = max(phrase_bonus, 0.24 + 0.06 * len(phrase.split()))

        # 3. Character-level similarity: cheap insurance against typos.
        fuzzy_score = SequenceMatcher(None, query_text, _normalise(entry.question)).ratio()

        score = (
            (0.55 * question_score)
            + (0.33 * keyword_score)
            + (0.12 * fuzzy_score)
            + phrase_bonus
        )
        return min(score, 1.0)

    def search(self, query: str, limit: int = MAX_SUGGESTIONS) -> list[tuple[FaqEntry, float]]:
        query_text = _normalise(query)[:MAX_QUERY_CHARS]
        query_tokens = set(_tokenise(query_text))
        scored = [
            (entry, self._score(query_tokens, query_text, entry)) for entry in self.entries
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [pair for pair in scored[:limit] if pair[1] > 0]


# --- Loading + caching -------------------------------------------------

_cache: FaqIndex | None = None
_cache_mtime: float | None = None
_cache_lock = Lock()


def _read_entries(path: Path) -> list[FaqEntry]:
    entries: list[FaqEntry] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            question = (row.get("question") or "").strip()
            answer = (row.get("answer") or "").strip()
            if not question or not answer:
                continue  # skip blank or half-filled rows rather than crashing

            keywords = [
                _normalise(part)
                for part in (row.get("keywords") or "").split("|")
                if part.strip()
            ]
            question_tokens = set(_tokenise(question))
            keyword_tokens = {token for kw in keywords for token in _tokenise(kw)}

            entries.append(
                FaqEntry(
                    id=(row.get("id") or str(len(entries) + 1)).strip(),
                    category=(row.get("category") or "general").strip(),
                    question=question,
                    answer=answer,
                    keywords=keywords,
                    question_tokens=question_tokens,
                    keyword_tokens=keyword_tokens,
                    all_tokens=question_tokens | keyword_tokens,
                )
            )
    return entries


def get_index() -> FaqIndex:
    """
    Return the cached index, rebuilding it if the CSV changed on disk.

    The mtime check makes editing the CSV a live operation in development
    and costs one stat() call per request in production.
    """
    global _cache, _cache_mtime

    try:
        mtime = FAQ_CSV_PATH.stat().st_mtime
    except OSError:
        mtime = None

    with _cache_lock:
        if _cache is None or mtime != _cache_mtime:
            entries = _read_entries(FAQ_CSV_PATH) if mtime is not None else []
            _cache = FaqIndex(entries)
            _cache_mtime = mtime
        return _cache


# --- Public API used by the view --------------------------------------

FALLBACK_ANSWER = (
    "I could not find an answer to that in our FAQ. Try rewording it, pick one "
    "of the suggested topics, or use the Contact link in the footer to reach the "
    "support team — include your order reference if it is about a specific order."
)


def answer_question(query: str) -> dict:
    """Resolve a customer message to an FAQ answer plus suggestions."""
    index = get_index()
    if not index.entries:
        return {
            "matched": False,
            "confidence": 0.0,
            "answer": FALLBACK_ANSWER,
            "matched_question": "",
            "category": "",
            "suggestions": [],
        }

    results = index.search(query)
    if not results:
        return {
            "matched": False,
            "confidence": 0.0,
            "answer": FALLBACK_ANSWER,
            "matched_question": "",
            "category": "",
            "suggestions": [entry.question for entry in index.entries[:MAX_SUGGESTIONS]],
        }

    best_entry, best_score = results[0]
    suggestions = [entry.question for entry, score in results[1:] if score >= SUGGEST_THRESHOLD]

    if best_score >= CONFIDENT_THRESHOLD:
        return {
            "matched": True,
            "confidence": round(best_score, 3),
            "answer": best_entry.answer,
            "matched_question": best_entry.question,
            "category": best_entry.category,
            "suggestions": suggestions,
        }

    if best_score >= SUGGEST_THRESHOLD:
        # Not confident enough to assert an answer — offer the candidates.
        return {
            "matched": False,
            "confidence": round(best_score, 3),
            "answer": "I am not sure I understood that. Did you mean one of these?",
            "matched_question": "",
            "category": "",
            "suggestions": [best_entry.question] + suggestions,
        }

    # Below the suggest threshold nothing is close enough to be worth
    # offering — showing a random FAQ here reads as the bot guessing.
    return {
        "matched": False,
        "confidence": round(best_score, 3),
        "answer": FALLBACK_ANSWER,
        "matched_question": "",
        "category": "",
        "suggestions": [],
    }


def list_faqs(category: str | None = None) -> list[dict]:
    entries = get_index().entries
    if category:
        wanted = _normalise(category)
        entries = [entry for entry in entries if _normalise(entry.category) == wanted]
    return [entry.as_dict() for entry in entries]


def list_categories() -> list[str]:
    seen: list[str] = []
    for entry in get_index().entries:
        if entry.category not in seen:
            seen.append(entry.category)
    return seen
