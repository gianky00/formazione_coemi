import React from 'react';
import { motion } from 'framer-motion';
import { Keyboard, Command, MousePointer2 } from 'lucide-react';

const Shortcut = ({ keys, desc }) => (
  <div className="flex items-center justify-between p-4 border-b border-gray-100 last:border-0 hover:bg-gray-50 transition-colors">
    <div className="text-gray-700 font-medium">{desc}</div>
    <div className="flex gap-2">
      {keys.map((k, i) => (
        <kbd key={i} className="px-2 py-1 bg-gray-100 border border-gray-300 rounded-md text-xs font-mono text-gray-600 shadow-sm">
          {k}
        </kbd>
      ))}
    </div>
  </div>
);

const ShortcutsGuide = () => {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-pink-100 rounded-lg text-pink-700">
            <Keyboard size={24} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Scorciatoie & Comandi</h1>
        </div>
        <p className="text-lg text-gray-500 ml-14">
          Velocizza il tuo lavoro utilizzando mouse e tastiera in modo esperto.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex items-center gap-2">
             <MousePointer2 size={18} className="text-gray-500" />
             <h3 className="font-bold text-gray-800">Tabelle (Database e Convalida)</h3>
          </div>
          <Shortcut keys={['CTRL', 'Click']} desc="Selezione Multipla (Aggiungi righe singole)" />
          <Shortcut keys={['SHIFT', 'Click']} desc="Selezione Intervallo (Da... A...)" />
          <Shortcut keys={['Click']} desc="Selezione Singola" />
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex items-center gap-2">
             <Command size={18} className="text-gray-500" />
             <h3 className="font-bold text-gray-800">Importazione</h3>
          </div>
          <Shortcut keys={['Drag', 'Drop']} desc="Trascina file o cartelle per importare" />
        </div>

      </div>

      <div className="mt-8 p-4 bg-blue-50 text-blue-800 rounded-lg border border-blue-100 text-sm">
          <strong>Nota:</strong> Al momento l'applicazione privilegia l'interazione via mouse per evitare errori accidentali (come cancellazioni involontarie tramite tastiera).
      </div>
    </div>
  );
};

export default ShortcutsGuide;
