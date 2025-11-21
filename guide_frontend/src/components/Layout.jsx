import React from 'react';
import Sidebar from './Sidebar';
import { Outlet } from 'react-router-dom';

const Layout = () => {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-intelleo-bg text-intelleo-text">
      <Sidebar />
      <main className="flex-1 overflow-y-auto relative scroll-smooth">
        <div className="p-8 max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
