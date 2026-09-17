import { useCallback, useEffect, useRef, useState } from 'react';
import { MessageCircle, X, Send, Bot, RotateCcw } from 'lucide-react';
import { supportApi } from '../../api/support';
import { cn } from '../../utils/cn';

/**
 * Floating FAQ assistant for the storefront.
 *
 * Mounted once in MainLayout so it follows the customer across every
 * public and customer-facing page instead of being re-mounted (and losing
 * its transcript) on each route change.
 *
 * Deliberately self-contained: conversation state lives in this component,
 * not in a context provider, because nothing outside the widget reads it.
 * If a future feature needs the transcript elsewhere, lift it then.
 */

const GREETING = {
  id: 'greeting',
  role: 'bot',
  text:
    "Hi! I'm the ShopNest assistant. Ask me about orders, payments, delivery, " +
    'returns or your account — or pick one of the questions below.',
};

let messageCounter = 0;
const nextId = () => `m${(messageCounter += 1)}`;

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([GREETING]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [starters, setStarters] = useState([]);

  const scrollRef = useRef(null);
  const inputRef = useRef(null);
  const panelRef = useRef(null);

  // Load a handful of starter questions the first time the panel opens, so
  // the request never fires for visitors who ignore the widget entirely.
  useEffect(() => {
    if (!isOpen || starters.length > 0) return;
    let cancelled = false;

    supportApi
      .listFaqs()
      .then((faqs) => {
        if (cancelled || !Array.isArray(faqs)) return;
        // One question per category, so the chips span topics instead of
        // showing four variations of the same thing.
        const seen = new Set();
        const spread = [];
        for (const faq of faqs) {
          if (seen.has(faq.category)) continue;
          seen.add(faq.category);
          spread.push(faq.question);
          if (spread.length === 4) break;
        }
        setStarters(spread);
      })
      .catch(() => {
        // Starter chips are a nicety — a failure here should not surface
        // an error to someone who has not asked anything yet.
      });

    return () => {
      cancelled = true;
    };
  }, [isOpen, starters.length]);

  // Keep the newest message in view.
  useEffect(() => {
    if (!isOpen) return;
    const node = scrollRef.current;
    if (node) node.scrollTop = node.scrollHeight;
  }, [messages, isOpen, isSending]);

  // Focus the input when the panel opens; close on Escape.
  useEffect(() => {
    if (!isOpen) return;
    inputRef.current?.focus();

    const onKeyDown = (event) => {
      if (event.key === 'Escape') setIsOpen(false);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [isOpen]);

  const send = useCallback(
    async (rawText) => {
      const text = (rawText ?? '').trim();
      if (!text || isSending) return;

      setMessages((prev) => [...prev, { id: nextId(), role: 'user', text }]);
      setInput('');
      setIsSending(true);

      try {
        const data = await supportApi.ask(text);
        setMessages((prev) => [
          ...prev,
          {
            id: nextId(),
            role: 'bot',
            text: data.answer,
            suggestions: data.suggestions ?? [],
          },
        ]);
      } catch (error) {
        const isRateLimited = error?.response?.status === 429;
        setMessages((prev) => [
          ...prev,
          {
            id: nextId(),
            role: 'bot',
            isError: true,
            text: isRateLimited
              ? 'That was a lot of questions at once — give it a minute and try again.'
              : 'Something went wrong reaching support. Please try again in a moment.',
          },
        ]);
      } finally {
        setIsSending(false);
        inputRef.current?.focus();
      }
    },
    [isSending]
  );

  const handleSubmit = (event) => {
    event.preventDefault();
    send(input);
  };

  const reset = () => {
    setMessages([GREETING]);
    setInput('');
    inputRef.current?.focus();
  };

  return (
    <>
      {/* Launcher */}
      <button
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        aria-expanded={isOpen}
        aria-controls="faq-chat-panel"
        aria-label={isOpen ? 'Close support chat' : 'Open support chat'}
        className={cn(
          'fixed bottom-5 right-5 z-40 flex h-14 w-14 items-center justify-center rounded-full',
          'bg-ember-500 text-white shadow-raised transition-transform duration-150',
          'hover:bg-ember-600 active:scale-95',
          'focus:outline-none focus:ring-2 focus:ring-ember-400 focus:ring-offset-2'
        )}
      >
        {isOpen ? (
          <X className="h-6 w-6" aria-hidden="true" />
        ) : (
          <MessageCircle className="h-6 w-6" aria-hidden="true" />
        )}
      </button>

      {/* Panel */}
      {isOpen && (
        <div
          id="faq-chat-panel"
          ref={panelRef}
          role="dialog"
          aria-label="Support chat"
          className={cn(
            'fixed bottom-24 right-5 z-40 flex w-[22rem] max-w-[calc(100vw-2.5rem)] flex-col',
            'h-[30rem] max-h-[calc(100vh-8rem)] overflow-hidden rounded-2xl',
            'border border-ink-100 bg-canvas-raised shadow-popover animate-slide-up'
          )}
        >
          {/* Header */}
          <header className="flex items-center gap-3 border-b border-ink-100 bg-ink-900 px-4 py-3 text-white">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-ember-500">
              <Bot className="h-4 w-4" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="font-display text-sm font-semibold leading-tight">Support assistant</p>
              <p className="text-xs text-ink-200">Answers common questions instantly</p>
            </div>
            <button
              type="button"
              onClick={reset}
              aria-label="Start a new conversation"
              className="rounded-md p-1.5 text-ink-200 transition-colors hover:bg-ink-800 hover:text-white"
            >
              <RotateCcw className="h-4 w-4" aria-hidden="true" />
            </button>
          </header>

          {/* Transcript */}
          <div
            ref={scrollRef}
            role="log"
            aria-live="polite"
            className="flex-1 space-y-3 overflow-y-auto px-4 py-4"
          >
            {messages.map((message) => (
              <div key={message.id} className="space-y-2">
                <div
                  className={cn(
                    'max-w-[85%] rounded-xl px-3 py-2 text-sm leading-relaxed',
                    message.role === 'user'
                      ? 'ml-auto bg-ember-500 text-white'
                      : message.isError
                        ? 'bg-danger-50 text-danger-700'
                        : 'bg-ink-50 text-ink-800'
                  )}
                >
                  {message.text}
                </div>

                {message.role === 'bot' && message.suggestions?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {message.suggestions.map((suggestion) => (
                      <button
                        key={suggestion}
                        type="button"
                        onClick={() => send(suggestion)}
                        className="rounded-full border border-ink-200 bg-white px-3 py-1 text-left text-xs text-ink-700 transition-colors hover:border-ember-300 hover:bg-ember-50 hover:text-ember-700"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {/* Starter chips, only while the conversation is untouched */}
            {messages.length === 1 && starters.length > 0 && (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {starters.map((question) => (
                  <button
                    key={question}
                    type="button"
                    onClick={() => send(question)}
                    className="rounded-full border border-ink-200 bg-white px-3 py-1 text-left text-xs text-ink-700 transition-colors hover:border-ember-300 hover:bg-ember-50 hover:text-ember-700"
                  >
                    {question}
                  </button>
                ))}
              </div>
            )}

            {isSending && (
              <div className="flex w-16 items-center gap-1 rounded-xl bg-ink-50 px-3 py-3">
                {[0, 150, 300].map((delay) => (
                  <span
                    key={delay}
                    className="h-1.5 w-1.5 animate-bounce rounded-full bg-ink-400"
                    style={{ animationDelay: `${delay}ms` }}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Composer */}
          <form
            onSubmit={handleSubmit}
            className="flex items-center gap-2 border-t border-ink-100 bg-canvas-soft px-3 py-3"
          >
            <label htmlFor="faq-chat-input" className="sr-only">
              Type your question
            </label>
            <input
              id="faq-chat-input"
              ref={inputRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask a question…"
              maxLength={500}
              autoComplete="off"
              className="h-10 flex-1 rounded-lg border border-ink-200 bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400 focus:border-ember-400 focus:outline-none focus:ring-1 focus:ring-ember-400"
            />
            <button
              type="submit"
              disabled={isSending || !input.trim()}
              aria-label="Send question"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-ember-500 text-white transition-colors hover:bg-ember-600 disabled:pointer-events-none disabled:opacity-50"
            >
              <Send className="h-4 w-4" aria-hidden="true" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
