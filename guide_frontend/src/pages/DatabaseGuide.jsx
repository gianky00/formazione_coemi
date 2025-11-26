import React from 'react';
import { motion } from 'framer-motion';
import DashboardSimulator from '../components/DashboardSimulator';
import { Info, AlertCircle, CheckCircle } from 'lucide-react';

const Section = ({ title, children }) => (
  <section className="mb-12">
    <h2 className="text-2xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">{title}</h2>
    <div className="text-gray-600 leading-relaxed space-y-4">
      {children}
    </div>
  </section>
);

const DatabaseGuide = () => {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-blue-100 rounded-lg text-intelleo-accent">
            <Info size={24} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Database Certificati</h1>
        </div>
        <p className="text-lg text-gray-500 ml-14">
          Il cuore del sistema. Visualizza, filtra e gestisci tutte le scadenze dei dipendenti in un'unica vista centralizzata.
        </p>
      </motion.div>

      {/* Interactive Simulator */}
      <Section title="Prova Interattiva">
        <p className="mb-4">
          Utilizza il simulatore qui sotto per prendere confidenza con l'interfaccia.
          <br/>
          <span className="text-sm text-blue-600 font-medium bg-blue-50 px-2 py-1 rounded">
            Obiettivo: Clicca su una riga per selezionarla e vedere i dettagli.
          </span>
        </p>
        <DashboardSimulator />
      </Section>

      {/* Detailed Guide */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Section title="Funzionalità Chiave">
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <CheckCircle size={20} className="text-green-500 mt-1 shrink-0" />
              <span>
                <strong>Monitoraggio Scadenze:</strong> La colonna <strong>Stato</strong> usa delle "pillole" colorate per mostrare a colpo d'occhio la situazione (Attivo, In Scadenza, Scaduto).
              </span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle size={20} className="text-green-500 mt-1 shrink-0" />
              <span>
                <strong>Filtri Avanzati:</strong> Utilizza i menu a tendina sopra la tabella per filtrare rapidamente per <strong>Dipendente</strong>, <strong>Categoria</strong>, o <strong>Stato</strong>.
              </span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle size={20} className="text-green-500 mt-1 shrink-0" />
              <span>
                <strong>Validazione:</strong> Visualizza solo i documenti che hanno superato il processo di validazione manuale.
              </span>
            </li>
          </ul>
        </Section>

        <Section title="Interazioni Avanzate">
          <div className="space-y-4">
             <div className="p-4 bg-white border border-gray-200 rounded-lg hover:border-blue-300 transition-colors">
                <h4 className="font-bold text-gray-800 mb-2">Modifica Rapida</h4>
                <p className="text-sm text-gray-600">
                   Seleziona una riga e clicca su <strong>Modifica</strong> per cambiare date o note.
                   Le modifiche vengono tracciate nel Log Attività.
                </p>
             </div>
             <div className="p-4 bg-white border border-gray-200 rounded-lg hover:border-red-300 transition-colors">
                <h4 className="font-bold text-gray-800 mb-2">Eliminazione Sicura</h4>
                <p className="text-sm text-gray-600">
                   Il tasto <strong>Cancella</strong> rimuove il certificato dal database.
                   Questa azione richiede conferma ed è irreversibile.
                </p>
             </div>
          </div>
        </Section>

        <Section title="Suggerimenti">
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg mb-4">
            <div className="flex items-start gap-3">
              <AlertCircle size={20} className="text-yellow-600 mt-1" />
              <div>
                <h4 className="font-bold text-yellow-800">Esportazione Dati</h4>
                <p className="text-sm text-yellow-700 mt-1">
                  Puoi esportare la vista corrente in formato CSV cliccando sul pulsante <strong>Esporta</strong>, posizionato accanto ai filtri.
                </p>
              </div>
            </div>
          </div>
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
            <div className="flex items-start gap-3">
              <Info size={20} className="text-blue-600 mt-1" />
              <div>
                <h4 className="font-bold text-blue-800">Selezione Multipla</h4>
                <p className="text-sm text-blue-700 mt-1">
                  Tieni premuto <code>CTRL</code> o <code>SHIFT</code> per selezionare più righe e cancellarle in un'unica operazione con il pulsante <strong>Cancella</strong>.
                </p>
              </div>
            </div>
          </div>
        </Section>
      </div>
    </div>
  );
};

export default DatabaseGuide;
