import { useEffect, useRef, useState } from 'react';
import { cn } from '../../utils/cn';

/**
 * Minimal accessible dropdown: click or Enter/Space to open, Escape or an
 * outside click to close, focus returns to the trigger on close. Used for
 * the account menu in the header and anywhere else a small action menu is
 * needed, so that behavior isn't reimplemented per-usage.
 */
export function DropdownMenu({ trigger, children, align = 'right', className }) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);
  const triggerRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;

    function handleClick(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false);
      }
    }
    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        setOpen(false);
        triggerRef.current?.focus();
      }
    }

    document.addEventListener('mousedown', handleClick);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClick);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [open]);

  return (
    <div ref={containerRef} className="relative">
      <button
        ref={triggerRef}
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((current) => !current)}
        className={className}
      >
        {trigger}
      </button>
      {open && (
        <div
          role="menu"
          className={cn(
            'absolute z-40 mt-2 min-w-[14rem] rounded-xl border border-ink-100 bg-white p-1.5 shadow-popover animate-slide-up',
            align === 'right' ? 'right-0' : 'left-0'
          )}
          onClick={() => setOpen(false)}
        >
          {children}
        </div>
      )}
    </div>
  );
}

export function DropdownMenuItem({ as: Component = 'button', className, ...props }) {
  return (
    <Component
      role="menuitem"
      className={cn(
        'flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-ink-700 hover:bg-ink-50',
        className
      )}
      {...props}
    />
  );
}

export function DropdownMenuSeparator() {
  return <div role="separator" className="my-1.5 h-px bg-ink-100" />;
}
