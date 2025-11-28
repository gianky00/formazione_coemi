import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import FeedbackFooter from './FeedbackFooter';
import { Outlet, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

const Layout = () => {
  const location = useLocation();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-intelleo-bg text-intelleo-text">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-y-auto relative scroll-smooth bg-gray-50/50">
          <div className="p-8 max-w-5xl mx-auto pb-24">
             <AnimatePresence mode="wait">
                <motion.div
                  key={location.pathname}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  transition={{ duration: 0.2, ease: "easeOut" }}
                >
                  <Outlet />
                  <FeedbackFooter />
                </motion.div>
             </AnimatePresence>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
