import { Link } from 'react-router-dom';
import { Compass } from 'lucide-react';
import { Button } from '../components/ui/Button';

export default function NotFoundPage() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center gap-4 px-4 py-24 text-center">
      <span className="flex h-14 w-14 items-center justify-center rounded-full bg-ink-100 text-ink-400">
        <Compass className="h-7 w-7" aria-hidden="true" />
      </span>
      <h1 className="font-display text-2xl font-bold text-ink-900">Page not found</h1>
      <p className="text-sm text-ink-500">
        The page you&rsquo;re looking for doesn&rsquo;t exist or may have moved.
      </p>
      <Button as={Link} to="/">
        Back to home
      </Button>
    </div>
  );
}
