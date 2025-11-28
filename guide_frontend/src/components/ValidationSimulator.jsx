import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, X, Eye, FileText, AlertCircle } from 'lucide-react';
import Badge from './ui/Badge';

const ValidationSimulator = () => {
  const [items, setItems] = useState([
    { id: 1, file: 'scansione_04.pdf', employee: 'BIANCHI LUCA', category: 'ANTINCENDIO', date: '2024-05-10', confidence: 'high' },
    { id: 2, file: 'doc_unknown_22.pdf', employee: '???', category: 'VISITA MEDICA', date: '2023-11-01', confidence: 'low' },
    { id: 3, file: 'cert_rossi.pdf', employee: 'ROSSI MARIO', category: 'PLE', date: '2022-01-15', confidence: 'medium' },
  ]);

  const [notification, setNotification] = useState(null);

  const handleApprove = (id) => {
    setItems(items.filter(i => i.id !== id));
    showNotification("Certificato approvato e spostato nel Database!", "success");
  };

  const handleReject = (id) => {
    setItems(items.filter(i => i.id !== id));
    showNotification("Certificato eliminato.", "error");
  };

  const showNotification = (msg, type) => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 3000);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden flex flex-col not-prose font-sans h-[400px] relative">

      {/* Header */}
      <div className="bg-gray-50 p-4 border-b border-gray-200 flex justify-between items-center">
        <h3 className="font-semibold text-gray-700 flex items-center gap-2">
            <AlertCircle size={18} className="text-orange-500"/>
            Coda di Convalida ({items.length})
        </h3>
        <span className="text-xs text-gray-400">Clicca ✓ per approvare, ✕ per rifiutare</span>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50/30">
        <AnimatePresence>
          {items.length > 0 ? (
            items.map((item) => (
              <motion.div
                key={item.id}
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20, height: 0, marginBottom: 0 }}
                className="bg-white border border-gray-200 rounded-lg p-4 mb-3 shadow-sm hover:shadow-md transition-shadow flex items-center justify-between gap-4 group"
              >
                {/* File Icon */}
                <div className="w-10 h-10 bg-red-50 text-red-500 rounded-lg flex items-center justify-center shrink-0">
                    <FileText size={20} />
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                        <span className={`font-bold text-sm truncate ${item.employee === '???' ? 'text-red-500 italic' : 'text-gray-900'}`}>
                            {item.employee}
                        </span>
                        {item.confidence === 'low' && <Badge variant="danger">Dati Incerti</Badge>}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span className="bg-gray-100 px-1.5 py-0.5 rounded text-gray-600">{item.category}</span>
                        <span>{item.date}</span>
                        <span className="text-gray-400 truncate max-w-[100px]">{item.file}</span>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                    <button className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors" title="Anteprima PDF">
                        <Eye size={18} />
                    </button>
                    <div className="w-px h-6 bg-gray-200 mx-1"></div>
                    <button
                        onClick={() => handleReject(item.id)}
                        className="p-2 text-red-500 hover:bg-red-50 rounded-full transition-colors"
                        title="Rifiuta/Elimina"
                    >
                        <X size={18} />
                    </button>
                    <button
                        onClick={() => handleApprove(item.id)}
                        className="p-2 bg-green-500 text-white hover:bg-green-600 rounded-full shadow-sm transition-colors hover:scale-105 active:scale-95"
                        title="Approva"
                    >
                        <Check size={18} />
                    </button>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <Check size={48} className="mb-4 text-green-200" />
                <p>Tutto fatto! Nessun documento in attesa.</p>
                <button onClick={() => window.location.reload()} className="mt-4 text-xs text-blue-500 underline">
                    Ricarica simulazione
                </button>
            </div>
          )}
        </AnimatePresence>
      </div>

      {/* Toast Notification */}
      <AnimatePresence>
        {notification && (
            <motion.div
                initial={{ y: 50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: 50, opacity: 0 }}
                className={`absolute bottom-4 left-1/2 transform -translate-x-1/2 px-4 py-2 rounded-full text-sm font-medium shadow-lg whitespace-nowrap ${
                    notification.type === 'success' ? 'bg-green-600 text-white' : 'bg-gray-800 text-white'
                }`}
            >
                {notification.msg}
            </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ValidationSimulator;
