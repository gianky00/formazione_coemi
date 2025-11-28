import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Lock, Activity, Globe, Smartphone, User } from 'lucide-react';

const SeverityBadge = ({ severity }) => {
  const styles = {
    LOW: 'bg-green-100 text-green-800 border-green-200',
    MEDIUM: 'bg-orange-100 text-orange-800 border-orange-200',
    CRITICAL: 'bg-red-100 text-red-800 border-red-200',
  };

  return (
    <span className={`px-2 py-0.5 rounded text-xs font-bold border ${styles[severity] || styles.LOW}`}>
      {severity}
    </span>
  );
};

const AuditSimulator = () => {
  const [filter, setFilter] = useState('ALL');
  const [selectedLog, setSelectedLog] = useState(null);

  const logs = [
    {
      id: 1,
      timestamp: '2023-10-27 09:15:22',
      severity: 'LOW',
      user: 'm.rossi',
      ip: '192.168.1.45',
      action: 'LOGIN_SUCCESS',
      category: 'AUTH',
      details: 'Accesso effettuato correttamente da postazione fissa.'
    },
    {
      id: 2,
      timestamp: '2023-10-27 10:30:05',
      severity: 'LOW',
      user: 'm.rossi',
      ip: '192.168.1.45',
      action: 'CERTIFICATE_UPDATE',
      category: 'DATA',
      details: 'Modificato certificato ID #452. [Data Scadenza: 2024-01-01 -> 2025-01-01]'
    },
    {
      id: 3,
      timestamp: '2023-10-27 14:12:00',
      severity: 'CRITICAL',
      user: 'unknown',
      ip: '45.22.11.1',
      action: 'BRUTE_FORCE_ATTEMPT',
      category: 'SECURITY',
      details: '5 tentativi di login falliti in 60 secondi. IP bloccato temporaneamente.'
    },
    {
      id: 4,
      timestamp: '2023-10-27 15:45:30',
      severity: 'MEDIUM',
      user: 'admin',
      ip: '192.168.1.10',
      action: 'CONFIG_CHANGE',
      category: 'CONFIG',
      details: 'Modificati parametri SMTP. [Host: vecchio -> smtp.gmail.com]'
    },
    {
        id: 5,
        timestamp: '2023-10-27 16:20:11',
        severity: 'LOW',
        user: 'm.rossi',
        ip: '192.168.1.45',
        action: 'EXPORT_CSV',
        category: 'DATA',
        details: 'Esportazione anagrafica dipendenti completata.'
      }
  ];

  const filteredLogs = filter === 'ALL'
    ? logs
    : logs.filter(log => {
        if (filter === 'SECURITY') return log.severity === 'CRITICAL' || log.severity === 'MEDIUM';
        return log.category === filter;
      });

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden flex flex-col h-[500px]">
      {/* Toolbar */}
      <div className="bg-gray-50 p-4 border-b border-gray-200">
        <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
          <button
            onClick={() => setFilter('ALL')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${filter === 'ALL' ? 'bg-blue-600 text-white shadow-sm' : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-100'}`}
          >
            Tutti
          </button>
          <button
            onClick={() => setFilter('SECURITY')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-1 ${filter === 'SECURITY' ? 'bg-red-600 text-white shadow-sm' : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-100'}`}
          >
            <Shield size={14} /> Security
          </button>
          <button
            onClick={() => setFilter('AUTH')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-1 ${filter === 'AUTH' ? 'bg-green-600 text-white shadow-sm' : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-100'}`}
          >
            <Lock size={14} /> Accessi
          </button>
           <button
            onClick={() => setFilter('DATA')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-1 ${filter === 'DATA' ? 'bg-purple-600 text-white shadow-sm' : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-100'}`}
          >
            <Activity size={14} /> Dati
          </button>
        </div>
      </div>

      {/* Table Header */}
      <div className="grid grid-cols-12 bg-gray-100 p-3 text-xs font-semibold text-gray-500 uppercase tracking-wider border-b border-gray-200">
        <div className="col-span-3">Data/Ora</div>
        <div className="col-span-2 text-center">Livello</div>
        <div className="col-span-2">Utente</div>
        <div className="col-span-2">IP</div>
        <div className="col-span-3">Azione</div>
      </div>

      {/* Table Body */}
      <div className="overflow-y-auto flex-1">
        {filteredLogs.map((log) => (
          <div key={log.id}>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              onClick={() => setSelectedLog(selectedLog === log.id ? null : log.id)}
              className={`grid grid-cols-12 p-3 text-xs border-b border-gray-100 cursor-pointer transition-colors items-center ${
                selectedLog === log.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : 'hover:bg-gray-50 border-l-4 border-l-transparent'
              }`}
            >
              <div className="col-span-3 text-gray-600 font-mono">{log.timestamp}</div>
              <div className="col-span-2 flex justify-center"><SeverityBadge severity={log.severity} /></div>
              <div className="col-span-2 font-medium text-gray-800">{log.user}</div>
              <div className="col-span-2 text-gray-500 font-mono text-[10px]">{log.ip}</div>
              <div className="col-span-3 font-semibold text-gray-700 truncate" title={log.action}>{log.action}</div>
            </motion.div>

            {/* Details Row */}
            <AnimatePresence>
                {selectedLog === log.id && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="bg-gray-50 border-b border-gray-200 overflow-hidden"
                    >
                        <div className="p-4 text-sm text-gray-700 font-mono bg-slate-50 border-t border-gray-200 shadow-inner">
                            <div className="flex items-center gap-2 mb-2 text-blue-600 font-bold uppercase text-xs">
                                <Activity size={14} /> Dettagli Evento
                            </div>
                            <p className="mb-2 leading-relaxed">{log.details}</p>
                            <div className="flex gap-4 mt-3 text-xs text-gray-500 border-t border-gray-200 pt-2">
                                <span className="flex items-center gap-1"><Globe size={12}/> Geo: Italia (Stimato)</span>
                                <span className="flex items-center gap-1"><Smartphone size={12}/> Device: PC-UFFICIO-01</span>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AuditSimulator;
