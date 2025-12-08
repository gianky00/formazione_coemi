import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, FileText, CheckCircle, AlertTriangle, FolderOpen, RefreshCcw } from 'lucide-react';

const ImportSimulator = () => {
  const [step, setStep] = useState('idle'); // idle, uploading, processing, done
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);

  const addLog = (msg, type) => {
    setLogs(prev => [...prev, { msg, type, id: Date.now() }]);
  };

  const simulateProcess = () => {
    setStep('uploading');
    setProgress(0);
    setLogs([]);

    // Simulate upload
    setTimeout(() => {
      setStep('processing');
      addLog('Caricamento completato. Avvio analisi AI...', 'info');

      let p = 0;
      const interval = setInterval(() => {
        p += 5;
        setProgress(p);

        if (p === 20) addLog('Analisi: doc_scan_001.pdf -> ROSSI MARIO (PLE)', 'success');
        if (p === 45) addLog('Analisi: doc_scan_002.pdf -> BIANCHI LUCA (ANTINCENDIO)', 'success');
        if (p === 70) addLog('Analisi: doc_unknown.pdf -> Dati incompleti (Orfano)', 'warning');
        if (p === 90) addLog('Spostamento file e rinomina in corso...', 'info');

        if (p >= 100) {
          clearInterval(interval);
          setStep('done');
          addLog('Operazione completata con successo.', 'done');
        }
      }, 150);
    }, 800);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
        simulateProcess();
    }
  };

  const reset = () => {
    setStep('idle');
    setProgress(0);
    setLogs([]);
  };

  const getLogColor = (type) => {
      if (type === 'error') return 'text-red-400';
      if (type === 'warning') return 'text-orange-300';
      if (type === 'success') return 'text-green-400';
      if (type === 'done') return 'text-blue-300 font-bold';
      return 'text-gray-300';
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden flex flex-col not-prose font-sans h-[450px]">

      {/* Header */}
      <div className="bg-gray-50 p-4 border-b border-gray-200 flex justify-between items-center">
        <div className="flex items-center gap-2">
           <div className="bg-purple-100 text-purple-700 p-1.5 rounded-md">
             <FileText size={18} />
           </div>
           <span className="font-semibold text-gray-700">Simulatore Importazione</span>
        </div>
        {step === 'done' && (
          <button
            onClick={reset}
            className="text-xs flex items-center gap-1 text-gray-500 hover:text-blue-600 transition-colors"
          >
            <RefreshCcw size={14} /> Riavvia
          </button>
        )}
      </div>

      {/* Main Area */}
      <div className="flex-1 p-6 flex flex-col items-center justify-center bg-gray-50/30 relative">

        <AnimatePresence mode="wait">
          {step === 'idle' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="text-center w-full max-w-md"
            >
              <button
                onClick={simulateProcess}
                onKeyDown={handleKeyDown}
                className="w-full border-2 border-dashed border-blue-300 rounded-xl p-10 bg-blue-50/50 hover:bg-blue-50 hover:border-blue-500 transition-all cursor-pointer group"
              >
                <UploadCloud size={48} className="mx-auto text-blue-400 group-hover:text-blue-600 mb-4 transition-colors" />
                <h3 className="text-lg font-bold text-gray-700 mb-2">Trascina qui i tuoi file PDF</h3>
                <p className="text-sm text-gray-500 mb-6">oppure clicca per selezionare una cartella</p>
                <span className="bg-blue-600 text-white px-6 py-2 rounded-lg text-sm font-medium shadow-sm group-hover:bg-blue-700 transition-colors inline-block">
                  Seleziona File
                </span>
              </button>
            </motion.div>
          )}

          {(step === 'uploading' || step === 'processing' || step === 'done') && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="w-full h-full flex flex-col"
            >
              {/* Progress Section */}
              <div className="mb-6 w-full max-w-lg mx-auto text-center">
                <div className="flex justify-between text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">
                  <span>Analisi in corso...</span>
                  <span>{progress}%</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-blue-600"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ ease: "linear" }}
                  />
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  Stima tempo rimanente: {step === 'done' ? '0s' : '2s'}
                </p>
              </div>

              {/* Console Output */}
              <div className="flex-1 bg-gray-900 rounded-lg p-4 font-mono text-xs overflow-y-auto custom-scrollbar border border-gray-800 shadow-inner w-full">
                {logs.map((log) => (
                  <motion.div
                    key={log.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`mb-1.5 flex items-center gap-2 ${getLogColor(log.type)}`}
                  >
                    <span>
                        {log.type === 'success' && <CheckCircle size={12} />}
                        {log.type === 'warning' && <AlertTriangle size={12} />}
                        {log.type === 'info' && <span className="w-3 block"></span>}
                        {log.type === 'done' && <CheckCircle size={12} />}
                    </span>
                    {log.msg}
                  </motion.div>
                ))}
                {step === 'processing' && (
                  <motion.span
                    animate={{ opacity: [0, 1, 0] }}
                    transition={{ repeat: Infinity, duration: 0.8 }}
                    className="text-blue-500"
                  >
                    _
                  </motion.span>
                )}
              </div>

              {step === 'done' && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3"
                  >
                      <FolderOpen className="text-green-600 mt-0.5" size={18} />
                      <div>
                          <h4 className="text-sm font-bold text-green-800">Analisi Terminata</h4>
                          <p className="text-xs text-green-700">3 file elaborati. 2 successi, 1 da convalidare.</p>
                      </div>
                  </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ImportSimulator;
