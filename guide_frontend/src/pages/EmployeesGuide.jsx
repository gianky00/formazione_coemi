import React from 'react';
import { motion } from 'framer-motion';
import { Users, Upload, Link, Search } from 'lucide-react';

const Section = ({ title, children }) => (
  <section className="mb-12">
    <h2 className="text-2xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">{title}</h2>
    <div className="text-gray-600 leading-relaxed space-y-4">
      {children}
    </div>
  </section>
);

const EmployeesGuide = () => {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-blue-100 rounded-lg text-blue-700">
            <Users size={24} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Gestione Dipendenti</h1>
        </div>
        <p className="text-lg text-gray-500 ml-14">
          Il registro centrale di tutto il personale. Mantieni i dati anagrafici sempre aggiornati per garantire associazioni corrette.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Section title="Anagrafica">
          <p>
            La sezione Dipendenti funge da "Master Data" per l'intera applicazione.
          </p>
          <ul className="space-y-3 mt-4">
            <li className="flex items-start gap-3">
              <Search size={20} className="text-gray-400 mt-1 shrink-0" />
              <span>
                <strong>Ricerca:</strong> Trova rapidamente un dipendente per Matricola o Nome.
              </span>
            </li>
            <li className="flex items-start gap-3">
              <Link size={20} className="text-gray-400 mt-1 shrink-0" />
              <span>
                <strong>Associazione:</strong> I certificati vengono collegati ai dipendenti tramite la <strong>Matricola</strong>. È fondamentale che sia univoca.
              </span>
            </li>
          </ul>
        </Section>

        <Section title="Importazione Massiva">
          <div className="bg-indigo-50 p-5 rounded-lg border border-indigo-100">
            <div className="flex items-center gap-2 text-indigo-800 font-bold mb-3">
              <Upload size={20} /> Import CSV
            </div>
            <p className="text-sm text-indigo-900 mb-3">
              Puoi caricare o aggiornare l'intera lista dipendenti caricando un file CSV formattato correttamente.
            </p>
            <div className="text-xs bg-white p-3 rounded border border-indigo-200 font-mono text-indigo-700">
              Cognome;Nome;Data_nascita;Badge<br/>
              ROSSI;MARIO;01/01/1980;12345
            </div>
            <p className="text-xs text-indigo-600 mt-2 italic">
              Nota: Il delimitatore deve essere il punto e virgola (;).
            </p>
          </div>
        </Section>
      </div>

      <Section title="Risoluzione Omonimie">
        <p>
          Intelleo gestisce automaticamente i casi di omonimia (stesso Nome e Cognome).
        </p>
        <p className="mt-2">
          Durante l'importazione dei certificati, se vengono trovati due dipendenti con lo stesso nome, il sistema utilizza la <strong>Data di Nascita</strong> estratta dal documento per identificare la persona corretta. Assicurati che le date di nascita siano presenti in anagrafica.
        </p>
      </Section>
    </div>
  );
};

export default EmployeesGuide;
