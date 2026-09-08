import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Search } from 'lucide-react';

/**
 * Header search box. Reads the current `?search=` value so it stays in
 * sync when someone lands on /products via a link, and always navigates to
 * /products on submit — search is a catalog-wide action, not scoped to
 * whatever page it's triggered from.
 */
export function SearchBar({ className }) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [value, setValue] = useState(searchParams.get('search') ?? '');

  function handleSubmit(event) {
    event.preventDefault();
    const params = new URLSearchParams();
    if (value.trim()) params.set('search', value.trim());
    navigate(`/products${params.toString() ? `?${params}` : ''}`);
  }

  return (
    <form role="search" onSubmit={handleSubmit} className={className}>
      <label htmlFor="site-search" className="sr-only">
        Search products
      </label>
      <div className="relative">
        <input
          id="site-search"
          type="search"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Search products, brands, categories…"
          className="h-11 w-full rounded-lg border border-transparent bg-white pl-4 pr-12 text-sm text-ink-900 placeholder:text-ink-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ember-400"
        />
        <button
          type="submit"
          aria-label="Search"
          className="absolute right-1.5 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-md bg-ember-500 text-white hover:bg-ember-600"
        >
          <Search className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
    </form>
  );
}
