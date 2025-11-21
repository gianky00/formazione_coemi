import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Filter, RefreshCw } from 'lucide-react';

const StatusPill = ({ status }) => {
  const styles = {
    attivo: 'bg-green-100 text-green-800 border-green-200',
    in_scadenza: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    scaduto: 'bg-red-100 text-red-800 border-red-200',
  };

  const labels = {
    attivo: 'Attivo',
    in_scadenza: 'In Scadenza',
    scaduto: 'Scaduto',
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${styles[status] || styles.attivo}`}>
      {labels[status] || status}
    </span>
  );
};

const DashboardSimulator = () => {
  const [selectedRow, setSelectedRow] = useState(null);
  const [searchText, setSearchText] = useState('');

  const data = [
    { id: 1, dipendente: 'ROSSI MARIO', corso: 'FORMAZIONE GENERALE', data: '15/05/2023', scadenza: '15/05/2028', stato: 'attivo' },
    { id: 2, dipendente: 'BIANCHI LUCA', corso: 'PRIMO SOCCORSO', data: '10/02/2021', scadenza: '10/02/2024', stato: 'scaduto' },
    { id: 3, dipendente: 'VERDI GIUSEPPE', corso: 'ANTINCENDIO', data: '20/11/2020', scadenza: '20/11/2025', stato: 'in_scadenza' },
    { id: 4, dipendente: 'FERRARI PAOLO', corso: 'PREPOSTO', data: '01/09/2022', scadenza: '01/09/2027', stato: 'attivo' },
  ];

  const filteredData = data.filter(item =>
    item.dipendente.toLowerCase().includes(searchText.toLowerCase()) ||
    item.corso.toLowerCase().includes(searchText.toLowerCase())
  );

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden flex flex-col h-[500px]">
      {/* Toolbar Mock */}
      <div className="bg-gray-50 p-4 border-b border-gray-200 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 flex-1 max-w-md bg-white border border-gray-300 rounded-md px-3 py-1.5 focus-within:ring-2 ring-blue-500/20">
          <Search size={16} className="text-gray-400" />
          <input
            type="text"
            placeholder="Cerca dipendente o corso..."
            className="w-full text-sm outline-none text-gray-700"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          <button className="p-2 text-gray-600 hover:bg-gray-200 rounded-md transition-colors">
            <Filter size={18} />
          </button>
          <button className="p-2 text-gray-600 hover:bg-gray-200 rounded-md transition-colors">
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {/* Table Header */}
      <div className="grid grid-cols-5 bg-gray-100 p-3 text-xs font-semibold text-gray-500 uppercase tracking-wider border-b border-gray-200">
        <div className="col-span-1">Dipendente</div>
        <div className="col-span-1">Corso</div>
        <div className="col-span-1">Data Rilascio</div>
        <div className="col-span-1">Data Scadenza</div>
        <div className="col-span-1 text-center">Stato</div>
      </div>

      {/* Table Body */}
      <div className="overflow-y-auto flex-1">
        {filteredData.map((row) => (
          <motion.div
            key={row.id}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onClick={() => setSelectedRow(row.id)}
            className={`grid grid-cols-5 p-3 text-sm border-b border-gray-100 cursor-pointer transition-colors ${
              selectedRow === row.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : 'hover:bg-gray-50 border-l-4 border-l-transparent'
            }`}
          >
            <div className="col-span-1 font-medium text-gray-900 flex items-center">{row.dipendente}</div>
            <div className="col-span-1 text-gray-600 flex items-center">{row.corso}</div>
            <div className="col-span-1 text-gray-500 flex items-center">{row.data}</div>
            <div className="col-span-1 text-gray-500 flex items-center">{row.scadenza}</div>
            <div className="col-span-1 flex items-center justify-center">
              <StatusPill status={row.stato} />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Interaction Feedback */}
      <AnimatePresence>
        {selectedRow && (
          <motion.div
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 50, opacity: 0 }}
            className="bg-blue-600 text-white text-sm py-2 px-4 text-center"
          >
            Hai selezionato: {data.find(d => d.id === selectedRow)?.dipendente}. I pulsanti di azione (Modifica/Cancella) ora sono attivi.
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DashboardSimulator;
