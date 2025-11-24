import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Book, Search, ChevronRight } from 'lucide-react';

const Term = ({ term, def }) => (
  <div className="border-b border-gray-100 py-4 hover:bg-gray-50 transition-colors px-4 rounded-lg">
    <h3 className="text-lg font-bold text-gray-900 mb-1">{term}</h3>
    <p className="text-gray-600 text-sm leading-relaxed">{def}</p>
  </div>
);

const Glossary = () => {
  const [filter, setFilter] = useState('');

  const terms = [
    {
      term: "AI (Intelligenza Artificiale)",
      def: "Il motore (Google Gemini 2.5 Pro) che legge e interpreta i documenti PDF. A differenza dell'OCR tradizionale, 'comprende' il contesto per estrarre date e nomi anche da formati non standard."
    },
    {
      term: "Audit Log",
      def: "Un registro digitale immutabile che traccia ogni operazione critica (login, modifica dati, esportazione). Serve per la conformità e la sicurezza."
    },
    {
      term: "Certificato Orfano",
      def: "Un documento che è stato analizzato con successo dall'AI, ma che non è stato possibile collegare automaticamente a un dipendente (spesso perché la matricola manca o è errata). Richiede un intervento manuale."
    },
    {
      term: "CSV",
      def: "Formato di file (Comma Separated Values) usato per importare massivamente l'anagrafica dipendenti. Intelleo richiede il separatore punto e virgola (;)."
    },
    {
      term: "Device ID",
      def: "Un'impronta digitale univoca che identifica il computer su cui è in esecuzione il software. Viene registrata nel Log Attività per sicurezza."
    },
    {
      term: "Lock File (.lock)",
      def: "Un file di sicurezza temporaneo che impedisce l'apertura simultanea del database da parte di due utenti diversi, prevenendo la corruzione dei dati."
    },
    {
      term: "Matricola (Badge)",
      def: "Il codice identificativo univoco del dipendente. È il dato fondamentale (Primary Key) che permette al sistema di collegare un certificato alla persona corretta."
    },
    {
      term: "Severità",
      def: "Il livello di gravità di un evento di sicurezza (LOW, MEDIUM, CRITICAL). Gli eventi CRITICAL (es. attacco Brute Force) scatenano un allarme via email."
    },
    {
      term: "SMTP",
      def: "Protocollo per l'invio delle email. Va configurato nelle impostazioni per permettere a Intelleo di inviare notifiche automatiche."
    },
    {
      term: "Stato: Validated",
      def: "Indica un certificato che è stato controllato e confermato da un operatore umano. Solo i certificati validati appaiono nello Scadenzario e nei Report."
    }
  ];

  const filteredTerms = terms.filter(t =>
    t.term.toLowerCase().includes(filter.toLowerCase()) ||
    t.def.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-indigo-100 rounded-lg text-indigo-700">
            <Book size={24} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Glossario</h1>
        </div>
        <p className="text-lg text-gray-500 ml-14 mb-8">
          Definizione dei termini tecnici e specifici utilizzati in Intelleo.
        </p>

        {/* Search Bar */}
        <div className="relative max-w-md mx-auto md:mx-0 ml-14">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Cerca un termine..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
          />
        </div>
      </motion.div>

      {/* Terms List */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
      >
        {filteredTerms.length > 0 ? (
          filteredTerms.map((item, index) => (
            <Term key={index} term={item.term} def={item.def} />
          ))
        ) : (
          <div className="p-8 text-center text-gray-500">
            Nessun termine trovato per "{filter}"
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default Glossary;
