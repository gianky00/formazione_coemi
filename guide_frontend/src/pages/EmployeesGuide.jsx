import React from 'react';
import { motion } from 'framer-motion';
import { Users, Upload, Link, Search, RefreshCw } from 'lucide-react';

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
            L'anagrafica dei dipendenti funge da "Master Data" (fonte di verità) per l'intera applicazione, garantendo che i certificati vengano associati alle persone corrette.
          </p>
          <ul className="space-y-3 mt-4">
            <li className="flex items-start gap-3">
              <Link size={20} className="text-gray-400 mt-1 shrink-0" />
              <span>
                <strong>Matricola Univoca:</strong> I documenti vengono collegati ai dipendenti tramite la <strong>Matricola</strong> (nel file CSV è la colonna `Badge`). È fondamentale che questo codice sia univoco per ogni dipendente.
              </span>
            </li>
          </ul>
        </Section>

        <Section title="Importazione Massiva & Recupero Orfani">
          <div className="bg-indigo-50 p-5 rounded-lg border border-indigo-100">
            <div className="flex items-center gap-2 text-indigo-800 font-bold mb-3">
              <Upload size={20} /> Import CSV
            </div>
            <p className="text-sm text-indigo-900 mb-3">
              Questa funzione esegue un <strong>"upsert"</strong>: aggiorna i dipendenti esistenti (in base alla matricola) e inserisce quelli nuovi, senza cancellare i dati non presenti nel file.
            </p>
            <div className="text-xs bg-white p-3 rounded border border-indigo-200 font-mono text-indigo-700">
              Cognome;Nome;Data_nascita;Badge<br/>
              ROSSI;MARIO;01/01/1980;12345
            </div>
            <p className="text-xs text-indigo-600 mt-2 italic">
             Nota: Il delimitatore deve essere il punto e virgola (;) e la dimensione massima del file è 5MB.
            </p>

            <div className="mt-4 pt-4 border-t border-indigo-200">
               <div className="flex items-center gap-2 text-indigo-800 font-bold mb-2">
                 <RefreshCw size={16} /> Link Automatico
               </div>
               <p className="text-sm text-indigo-900">
                 Al termine dell'importazione, il sistema scansiona automaticamente tutti i certificati "orfani" (non assegnati) nella vista <em>Convalida Dati</em> e tenta di collegarli ai nuovi dipendenti inseriti.
               </p>
            </div>
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
