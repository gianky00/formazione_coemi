import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, ZoomIn, Download, Mail } from 'lucide-react';

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

      <Section title="Struttura Gerarchica">
         <p>
           La barra laterale sinistra organizza i certificati in un albero logico:
         </p>
         <ul className="mt-2 space-y-2 text-sm text-gray-600 font-mono bg-gray-50 p-4 rounded border border-gray-200">
           <li>📂 DOCUMENTI DIPENDENTI</li>
           <li className="pl-4">📁 Categoria (es. ANTINCENDIO)</li>
           <li className="pl-8">📂 IN SCADENZA</li>
           <li className="pl-8">📂 SCADUTI</li>
           <li className="pl-12">👤 Dipendente (es. Rossi Mario)</li>
         </ul>
         <p className="mt-2 text-sm text-gray-500">
           Clicca su una categoria per filtrare il grafico e mostrare solo quel tipo di corso.
         </p>
      </Section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Section title="Navigazione Temporale">
          <ul className="space-y-4">
            <li className="flex items-start gap-3">
              <ZoomIn size={20} className="text-blue-500 mt-1 shrink-0" />
              <div>
                <strong>Zoom Timeline:</strong>
                <p className="text-sm text-gray-500 mt-1">
                  Usa i pulsanti <strong>3M</strong> (3 Mesi), <strong>6M</strong> (6 Mesi) o <strong>1Y</strong> (1 Anno) per cambiare la scala temporale.
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <Calendar size={20} className="text-blue-500 mt-1 shrink-0" />
              <div>
                <strong>Filtro Automatico:</strong>
                <p className="text-sm text-gray-500 mt-1">
                  Di default, il grafico mostra solo i certificati scaduti o in scadenza nei prossimi 90 giorni, per focalizzare l'attenzione sulle urgenze.
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
                <Mail size={18} /> Invia Email
              </div>
              <p className="text-sm text-gray-600">
                Invia manualmente un report via email ai destinatari configurati, contenente la lista delle scadenze imminenti.
              </p>
            </div>
          </div>
        </Section>
      </div>
    </div>
  );
};

export default CalendarGuide;
