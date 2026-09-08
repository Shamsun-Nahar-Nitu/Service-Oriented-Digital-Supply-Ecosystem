/**
 * Tiny classnames joiner. Filters out falsy values so conditional Tailwind
 * classes can be written as `cn('base', isActive && 'active')` without
 * pulling in a dependency for something this small.
 */
export function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}
