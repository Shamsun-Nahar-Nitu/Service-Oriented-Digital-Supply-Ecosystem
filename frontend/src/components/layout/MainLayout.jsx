import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { CategoryNav } from './CategoryNav';
import { Footer } from './Footer';
import { ChatWidget } from '../support/ChatWidget'; 

/** Shell for every public/customer-facing page: header, category strip, footer. */
export function MainLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-canvas">
      <Header />
      <CategoryNav />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
      <ChatWidget />
    </div>
  );
}
