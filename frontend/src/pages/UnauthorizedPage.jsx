import { Link } from 'react-router-dom';
import { ShieldAlert } from 'lucide-react';
import { Button } from '../components/ui/Button';

export default function UnauthorizedPage() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center gap-4 px-4 py-24 text-center">
      <span className="flex h-14 w-14 items-center justify-center rounded-full bg-danger-100 text-danger-600">
        <ShieldAlert className="h-7 w-7" aria-hidden="true" />
      </span>
      <h1 className="font-display text-2xl font-bold text-ink-900">You don&rsquo;t have access to this page</h1>
      <p className="text-sm text-ink-500">
        This area is restricted to a different account role. If you think this is a mistake,
        contact support.
      </p>
      <Button as={Link} to="/">
        Back to home
      </Button>
    </div>
  );
}
