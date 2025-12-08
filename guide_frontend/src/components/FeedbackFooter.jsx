import React, { useState, useEffect } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

const FeedbackFooter = () => {
  const location = useLocation();
  const [voted, setVoted] = useState(null); // 'up', 'down', or null

  // Reset vote on page change
  useEffect(() => {
    const storedVote = localStorage.getItem(`feedback_${location.pathname}`);
    setVoted(storedVote);
  }, [location.pathname]);

  const handleVote = (type) => {
    setVoted(type);
    localStorage.setItem(`feedback_${location.pathname}`, type);
  };

  return (
    <div className="mt-20 border-t border-gray-200 pt-8 pb-4">
      <div className="flex flex-col items-center justify-center text-center">

        <AnimatePresence mode="wait">
          {voted === null ? (
            <motion.div
              key="voting"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              <h4 className="text-sm font-semibold text-gray-900">Questa pagina ti è stata utile?</h4>
              <div className="flex gap-4">
                <button
                  onClick={() => handleVote('up')}
                  className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg hover:border-green-400 hover:text-green-600 hover:bg-green-50 transition-all group shadow-sm"
                >
                  <ThumbsUp size={16} className="text-gray-400 group-hover:text-green-600 transition-colors" />
                  <span className="text-sm font-medium text-gray-600 group-hover:text-green-700">Sì, grazie</span>
                </button>
                <button
                  onClick={() => handleVote('down')}
                  className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg hover:border-red-400 hover:text-red-600 hover:bg-red-50 transition-all group shadow-sm"
                >
                  <ThumbsDown size={16} className="text-gray-400 group-hover:text-red-600 transition-colors" />
                  <span className="text-sm font-medium text-gray-600 group-hover:text-red-700">Non molto</span>
                </button>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="thankyou"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-green-50 text-green-800 px-6 py-3 rounded-lg border border-green-100 shadow-sm"
            >
              <p className="text-sm font-medium">Grazie per il tuo feedback!</p>
            </motion.div>
          )}
        </AnimatePresence>

        <p className="text-xs text-gray-400 mt-6">
          Ultimo aggiornamento: 25 Gennaio 2025 • Intelleo v1.0
        </p>
      </div>
    </div>
  );
};

export default FeedbackFooter;
