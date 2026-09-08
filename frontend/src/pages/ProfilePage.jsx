import { useState } from 'react';
import { ProfileForm } from '../components/forms/ProfileForm';
import { ChangePasswordForm } from '../components/forms/ChangePasswordForm';
import { PageHeader } from '../components/ui/PageHeader';
import { cn } from '../utils/cn';

const TABS = [
  { id: 'profile', label: 'Profile' },
  { id: 'password', label: 'Password' },
];

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState('profile');

  return (
    <div className="mx-auto max-w-2xl px-4 py-6 sm:px-6">
      <PageHeader title="Account settings" />

      <div role="tablist" aria-label="Account settings sections" className="flex gap-1 border-b border-ink-100">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={activeTab === tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'border-b-2 px-4 py-2.5 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'border-ember-500 text-ink-900'
                : 'border-transparent text-ink-500 hover:text-ink-800'
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="mt-6 rounded-xl border border-ink-100 bg-white p-6">
        {activeTab === 'profile' ? <ProfileForm /> : <ChangePasswordForm />}
      </div>
    </div>
  );
}
