import React, { useRef, useEffect } from 'react';
import { Search, Command, X, ChevronRight } from 'lucide-react';
import { useSearch } from '../hooks/useSearch';
import { motion, AnimatePresence } from 'framer-motion';
import { useLocation, Link } from 'react-router-dom';

const Header = () => {
  const { query, setQuery, results, selectResult } = useSearch();
  const searchRef = useRef(null);
  const location = useLocation();

  // Breadcrumb logic
  const getBreadcrumb = () => {
    const path = location.pathname;
    if (path === '/') return 'Panoramica';

    // Simple mapping, can be expanded
    const map = {
      '/database': 'Database',
      '/import': 'Importazione',
      '/validation': 'Convalida',
      '/calendar': 'Scadenzario',
      '/employees': 'Dipendenti',
      '/security': 'Sicurezza',
      '/settings': 'Configurazione',
      '/maintenance': 'Manutenzione',
      '/troubleshooting': 'Supporto',
      '/glossary': 'Glossario',
      '/shortcuts': 'Scorciatoie',
    };
    return map[path] || 'Guida';
  };

  // Close search on click outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setQuery(''); // Clear/Close search
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [setQuery]);

  return (
    <header className="h-16 bg-white border-b border-gray-200 px-8 flex items-center justify-between sticky top-0 z-40 shadow-sm">

      {/* Breadcrumb */}
      <div className="flex items-center text-sm text-gray-500 font-medium">
        <Link to="/" className="hover:text-intelleo-accent transition-colors">Home</Link>
        {location.pathname !== '/' && (
          <>
            <ChevronRight size={14} className="mx-2 text-gray-400" />
            <span className="text-intelleo-text">{getBreadcrumb()}</span>
          </>
        )}
      </div>

      {/* Search Bar */}
      <div className="relative w-96" ref={searchRef}>
        <div className="relative">
          <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Cerca nella guida..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-10 pr-10 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
          {query ? (
             <button onClick={() => setQuery('')} className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600">
               <X size={14} />
             </button>
          ) : (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
              <span className="text-xs text-gray-400 font-mono border border-gray-200 rounded px-1">⌘K</span>
            </div>
          )}
        </div>

        {/* Search Results Dropdown */}
        <AnimatePresence>
          {query && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="absolute top-full mt-2 left-0 w-full bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden py-2"
            >
              {results.length > 0 ? (
                results.map((result) => (
                  <button
                    key={result.path}
                    onClick={() => selectResult(result.path)}
                    className="w-full text-left px-4 py-2.5 hover:bg-blue-50 flex items-center gap-3 transition-colors group"
                  >
                    <div className="p-1.5 bg-gray-100 rounded-md group-hover:bg-blue-200 text-gray-500 group-hover:text-blue-700 transition-colors">
                      <Command size={14} />
                    </div>
                    <span className="text-sm font-medium text-gray-700 group-hover:text-blue-900">{result.title}</span>
                  </button>
                ))
              ) : (
                <div className="px-4 py-6 text-center text-gray-500 text-sm">
                  Nessun risultato trovato.
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </header>
  );
};

export default Header;
