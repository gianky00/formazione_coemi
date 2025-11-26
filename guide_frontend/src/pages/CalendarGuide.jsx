import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, ZoomIn, Download, Mail, Send } from 'lucide-react';

const Section = ({ title, children }) => (
  <section className="mb-12">
    <h2 className="text-2xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">{title}</h2>
    <div className="text-gray-600 leading-relaxed space-y-4">
      {children}
    </div>
  </section>
);

const CalendarGuide = () => {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-green-100 rounded-lg text-green-700">
            <Calendar size={24} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Scadenzario Grafico</h1>
        </div>
        <p className="text-lg text-gray-500 ml-14">
          Pianifica le attività future con una timeline visiva (Gantt) chiara e intuitiva.
        </p>
      </motion.div>

      <Section title="Panoramica">
        <p>
          Lo Scadenzario Grafico offre una vista temporale di tutte le scadenze. A differenza della tabella classica, qui puoi vedere a colpo d'occhio la distribuzione del lavoro nel tempo.
        </p>
        <div className="flex flex-wrap gap-4 mt-4">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500"></span>
            <span className="text-sm font-medium">Scaduto</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-orange-400"></span>
            <span className="text-sm font-medium">In Scadenza (entro 60gg)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-500"></span>
            <span className="text-sm font-medium">Valido</span>
          </div>
        </div>
      </Section>

      <Section title="Flusso Dati Tecnico">
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 font-mono text-sm text-slate-700">
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-slate-200 px-2 py-0.5 rounded text-xs font-bold uppercase">Input</span>
              <span>Certificati Validati (Status: MANUAL)</span>
            </div>
            <div className="flex justify-center my-1 text-slate-400">↓</div>
            <div className="flex items-center gap-2">
              <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-xs font-bold uppercase">Output</span>
              <span>Visualizzazione Gantt & Report PDF (Email)</span>
            </div>
          </div>
      </Section>

      <Section title="Struttura Gerarchica dei File">
        <p>
          Dopo l'analisi, i file PDF vengono rinominati e organizzati in una struttura di cartelle standardizzata per garantire coerenza e facilità di accesso.
        </p>
        <div className="mt-4 bg-gray-50 p-6 rounded-lg border border-gray-200">
          <h4 className="font-semibold text-gray-700 mb-4">Esempio Struttura Cartelle:</h4>
          {/* Visual Diagram */}
          <div className="font-mono text-sm text-gray-600 space-y-2">
            <div className="flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-yellow-500"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"></path></svg>
              <span>DOCUMENTI DIPENDENTI</span>
            </div>
            <div className="flex items-center gap-2 pl-4">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-yellow-500"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"></path></svg>
              <span className="font-semibold">ROSSI MARIO (1045)</span>
            </div>
            <div className="flex items-center gap-2 pl-8">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-yellow-500"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"></path></svg>
              <span className="text-blue-600">PATENTI</span>
            </div>
             <div className="flex items-center gap-2 pl-12">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
              <span className="text-green-700">ROSSI MARIO (1045) - PATENTI - 15_07_2028.pdf</span>
            </div>
          </div>
        </div>
        <div className="mt-4 text-sm text-gray-500">
          <p><span className="font-semibold">Nota:</span> Il nome del file segue la convenzione <strong>NOME COGNOME (MATRICOLA) - CATEGORIA - SCADENZA.pdf</strong> per una facile identificazione.</p>
        </div>
      </Section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Section title="Navigazione Temporale">
          <ul className="space-y-4">
            <li className="flex items-start gap-3">
              <ZoomIn size={20} className="text-blue-500 mt-1 shrink-0" />
              <div>
                <strong>Zoom Timeline:</strong>
                <p className="text-sm text-gray-500 mt-1">
                  Usa i pulsanti <strong>3M</strong> (3 Mesi), <strong>6M</strong> (6 Mesi) o <strong>1Y</strong> (1 Anno) per cambiare la scala temporale. (Default: 3 Mesi)
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <Calendar size={20} className="text-blue-500 mt-1 shrink-0" />
              <div>
                <strong>Filtro Automatico:</strong>
                <p className="text-sm text-gray-500 mt-1">
                  Di default, il grafico mostra solo i documenti scaduti o in scadenza nei prossimi 90 giorni, per focalizzare l'attenzione sulle urgenze.
                </p>
              </div>
            </li>
          </ul>
        </Section>

        <Section title="Azioni Rapide">
          <div className="space-y-4">
            <div className="border-l-4 border-red-500 pl-4 py-1">
              <div className="flex items-center gap-2 font-bold text-gray-800 mb-1">
                <Download size={18} /> Esporta PDF
              </div>
              <p className="text-sm text-gray-600">
                Scarica un report visivo del grafico attuale, perfetto da stampare o inviare ai responsabili.
              </p>
            </div>
            <div className="border-l-4 border-blue-500 pl-4 py-1">
              <div className="flex items-center gap-2 font-bold text-gray-800 mb-1">
                <Send size={18} /> Genera Email
              </div>
              <p className="text-sm text-gray-600">
                Premendo il tasto <strong>"Genera Email"</strong>, il sistema invierà immediatamente un report PDF via email ai destinatari configurati, contenente la lista aggiornata delle scadenze.
              </p>
            </div>
          </div>
        </Section>
      </div>
    </div>
  );
};

export default CalendarGuide;
