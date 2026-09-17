import { apiClient } from './client';

/**
 * /support/ — public FAQ chatbot (apps/support/views.py).
 *
 * These endpoints are AllowAny, so they work for signed-out visitors too.
 * The shared apiClient still attaches a bearer token when one exists; the
 * backend ignores it for this app, which keeps a single axios instance and
 * a single base URL in play rather than a second client just for support.
 */
export const supportApi = {
  /** Ask a question. Resolves to { matched, confidence, answer, matched_question, category, suggestions }. */
  ask: (message) => apiClient.post('/support/chat/', { message }).then((res) => res.data),

  /** Full FAQ list, optionally filtered by category. Used for the starter chips. */
  listFaqs: (category) =>
    apiClient
      .get('/support/faqs/', { params: category ? { category } : undefined })
      .then((res) => res.data),

  /** Distinct FAQ categories, in CSV order. */
  listCategories: () =>
    apiClient.get('/support/faq-categories/').then((res) => res.data.categories),
};
