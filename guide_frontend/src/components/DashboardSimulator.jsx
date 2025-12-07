import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, RefreshCw, Edit2, Trash2 } from 'lucide-react';
import Badge from './ui/Badge';

const DashboardSimulator = () => {
  const [selectedRow, setSelectedRow] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  const initialData = [
    { id: 1, dipendente: 'ROSSI MARIO', corso: 'FORMAZIONE GENERALE', data: '15/05/2023', scadenza: '15/05/2028', stato: 'attivo' },
    { id: 2, dipendente: 'BIANCHI LUCA', corso: 'PRIMO SOCCORSO', data: '10/02/2021', scadenza: '10/02/2024', stato: 'scaduto' },
    { id: 3, dipendente: 'VERDI GIUSEPPE', corso: 'ANTINCENDIO', data: '20/11/2020', scadenza: '20/11/2025', stato: 'in_scadenza' },
    { id: 4, dipendente: 'FERRARI PAOLO', corso: 'PREPOSTO', data: '01/09/2022', scadenza: '01/09/2027', stato: 'attivo' },
    { id: 5, dipendente: 'NERI ALESSANDRO', corso: 'HLO', data: '12/03/2024', scadenza: '12/03/2029', stato: 'attivo' },
  ];

  // Filtering
  let processedData = initialData.filter(item =>
    item.dipendente.toLowerCase().includes(searchText.toLowerCase()) ||
    item.corso.toLowerCase().includes(searchText.toLowerCase())
  );

  // Sorting
  if (sortConfig.key) {
    processedData.sort((a, b) => {
      if (a[sortConfig.key] < b[sortConfig.key]) return sortConfig.direction === 'asc' ? -1 : 1;
      if (a[sortConfig.key] > b[sortConfig.key]) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const handleKeyDown = (e, key) => {
      if (e.key === 'Enter' || e.key === ' ') {
          handleSort(key);
      }
  };

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'asc' ? '↑' : '↓';
  };

  const getBadgeVariant = (stato) => {
      if (stato === 'attivo') return 'success';
      if (stato === 'in_scadenza') return 'warning';
      return 'danger';
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden flex flex-col h-[500px] not-prose font-sans">
      {/* Toolbar Mock */}
      <div className="bg-gray-50 p-4 border-b border-gray-200 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 w-full md:w-auto flex-1 max-w-md bg-white border border-gray-300 rounded-md px-3 py-1.5 focus-within:ring-2 ring-blue-500/20 shadow-sm">
          <Search size={16} className="text-gray-400" />
          <input
            type="text"
            placeholder="Cerca dipendente o corso..."
            className="w-full text-sm outline-none text-gray-700 placeholder:text-gray-400"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
        </div>
        <div className="flex gap-2 w-full md:w-auto justify-end">
          <button
            className="p-2 text-gray-600 hover:bg-white hover:shadow-sm border border-transparent hover:border-gray-200 rounded-md transition-all"
            title="Filtra (Simulato)"
          >
            <Filter size={18} />
          </button>
          <button
            className="p-2 text-gray-600 hover:bg-white hover:shadow-sm border border-transparent hover:border-gray-200 rounded-md transition-all"
            onClick={() => { setSearchText(''); setSortConfig({ key: null, direction: 'asc' }); }}
            title="Resetta"
          >
            <RefreshCw size={18} />
          </button>

          <div className="w-px h-8 bg-gray-300 mx-1"></div>

          <button
            disabled={!selectedRow}
            className={`p-2 rounded-md transition-all flex items-center gap-2 ${selectedRow ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-300 bg-gray-100 cursor-not-allowed'}`}
          >
            <Edit2 size={16} />
            <span className="text-xs font-semibold hidden md:inline">Modifica</span>
          </button>
           <button
            disabled={!selectedRow}
            className={`p-2 rounded-md transition-all flex items-center gap-2 ${selectedRow ? 'bg-red-600 text-white shadow-sm' : 'text-gray-300 bg-gray-100 cursor-not-allowed'}`}
          >
            <Trash2 size={16} />
             <span className="text-xs font-semibold hidden md:inline">Cancella</span>
          </button>
        </div>
      </div>

      {/* Table Header */}
      <div className="grid grid-cols-5 bg-gray-100 p-3 text-xs font-bold text-gray-500 uppercase tracking-wider border-b border-gray-200">
        <div
            className="col-span-1 cursor-pointer hover:text-gray-700"
            onClick={() => handleSort('dipendente')}
            onKeyDown={(e) => handleKeyDown(e, 'dipendente')}
            role="button"
            tabIndex={0}
        >
            Dipendente {getSortIcon('dipendente')}
        </div>
        <div
            className="col-span-1 cursor-pointer hover:text-gray-700"
            onClick={() => handleSort('corso')}
            onKeyDown={(e) => handleKeyDown(e, 'corso')}
            role="button"
            tabIndex={0}
        >
            Documento {getSortIcon('corso')}
        </div>
        <div
            className="col-span-1 cursor-pointer hover:text-gray-700"
            onClick={() => handleSort('data')}
            onKeyDown={(e) => handleKeyDown(e, 'data')}
            role="button"
            tabIndex={0}
        >
            Data Ril. {getSortIcon('data')}
        </div>
        <div
            className="col-span-1 cursor-pointer hover:text-gray-700"
            onClick={() => handleSort('scadenza')}
            onKeyDown={(e) => handleKeyDown(e, 'scadenza')}
            role="button"
            tabIndex={0}
        >
            Scadenza {getSortIcon('scadenza')}
        </div>
        <div className="col-span-1 text-center">Stato</div>
      </div>

      {/* Table Body */}
      <div className="overflow-y-auto flex-1 bg-white">
        {processedData.length > 0 ? (
            processedData.map((row) => (
            <motion.div
                key={row.id}
                layout
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                onClick={() => setSelectedRow(row.id === selectedRow ? null : row.id)}
                className={`grid grid-cols-5 p-3 text-sm border-b border-gray-100 cursor-pointer transition-all ${
                selectedRow === row.id
                    ? 'bg-blue-50 border-l-4 border-l-blue-600 shadow-inner'
                    : 'hover:bg-gray-50 border-l-4 border-l-transparent'
                }`}
            >
                <div className="col-span-1 font-semibold text-gray-900 flex items-center truncate pr-2" title={row.dipendente}>{row.dipendente}</div>
                <div className="col-span-1 text-gray-600 flex items-center truncate pr-2" title={row.corso}>{row.corso}</div>
                <div className="col-span-1 text-gray-500 flex items-center text-xs font-mono">{row.data}</div>
                <div className="col-span-1 text-gray-500 flex items-center text-xs font-mono">{row.scadenza}</div>
                <div className="col-span-1 flex items-center justify-center">
                   <Badge variant={getBadgeVariant(row.stato)}>
                      {row.stato.replace('_', ' ').toUpperCase()}
                   </Badge>
                </div>
            </motion.div>
            ))
        ) : (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <Search size={48} className="mb-2 opacity-20" />
                <p>Nessun risultato trovato</p>
            </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="bg-gray-50 border-t border-gray-200 p-2 text-xs text-gray-500 flex justify-between items-center">
          <span>{processedData.length} righe visualizzate</span>
          <div className="flex gap-2">
             <span className="w-2 h-2 rounded-full bg-green-500 inline-block"></span>
             {' '}Attivo
             <span className="w-2 h-2 rounded-full bg-yellow-500 inline-block"></span>
             {' '}In Scadenza
             <span className="w-2 h-2 rounded-full bg-red-500 inline-block"></span>
             {' '}Scaduto
          </div>
      </div>
    </div>
  );
};

export default DashboardSimulator;
