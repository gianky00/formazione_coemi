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
        <div className="flex flex-wrap gap-4 mt-4 bg-gray-50 p-3 rounded-lg border">
          <div className="flex items-center gap-2">
            <span className="w-4 h-4 rounded" style={{ backgroundColor: '#EF4444' }}></span>
            <span className="text-sm font-medium">Scaduto</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 h-4 rounded" style={{ backgroundColor: '#F97316' }}></span>
            <span className="text-sm font-medium">In scadenza (&lt; 30 gg)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 h-4 rounded" style={{ backgroundColor: '#FBBF24' }}></span>
            <span className="text-sm font-medium">Avviso (30-90 gg)</span>
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Section title="Navigazione e Interazione">
          <ul className="space-y-4">
            <li className="flex items-start gap-3">
              <ZoomIn size={20} className="text-blue-500 mt-1 shrink-0" />
              <div>
                <strong>Controlli Timeline:</strong>
                <p className="text-sm text-gray-500 mt-1">
                  Usa i pulsanti <strong>&lt;</strong> e <strong>&gt;</strong> per scorrere la timeline un mese alla volta. Cambia il livello di zoom (3 Mesi, 6 Mesi, 1 Anno) usando il menu a tendina dedicato.
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <Calendar size={20} className="text-blue-500 mt-1 shrink-0" />
              <div>
                <strong>Vista ad Albero:</strong>
                <p className="text-sm text-gray-500 mt-1">
                  Sulla sinistra, una vista ad albero raggruppa i certificati per <strong>Categoria</strong>, poi per <strong>Stato</strong> (In Scadenza / Scaduti) e infine per <strong>Dipendente</strong>. Clicca su un dipendente per evidenziare la sua barra corrispondente nel grafico.
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
