import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import FeedbackFooter from './FeedbackFooter';
import { Outlet } from 'react-router-dom';

const Layout = () => {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-intelleo-bg text-intelleo-text">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-y-auto relative scroll-smooth bg-gray-50/50">
          <div className="p-8 max-w-5xl mx-auto pb-24">
             {/* Animation removed to ensure stability in Qt WebEngine */}
             <Outlet />
             <FeedbackFooter />
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
