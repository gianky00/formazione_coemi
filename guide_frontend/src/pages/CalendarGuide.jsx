import React from 'react';
import GuideCard from '../components/ui/GuideCard';
import Note from '../components/ui/Note';
import Step from '../components/ui/Step';
import { Calendar, Clock, AlertTriangle, FileText, Mail } from 'lucide-react';

const CalendarGuide = () => {
  return (
    <div className="space-y-12">
      <div className="max-w-3xl">
        <h1 className="h1">Scadenzario Grafico</h1>
        <p className="text-body text-xl">
          Visualizza le scadenze nel tempo con un diagramma di Gantt interattivo. Pianifica rinnovi e formazione con mesi di anticipo.
        </p>
      </div>

      <section>
        <h2 className="h2">Panoramica Interfaccia</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <GuideCard title="Timeline (Gantt)" icon={Calendar}>
                <p>Una vista a barre orizzontali. Ogni barra rappresenta la durata di validità di un certificato. La lunghezza indica quanto manca alla scadenza.</p>
            </GuideCard>
            <GuideCard title="Colori di Stato" icon={AlertTriangle}>
                <ul className="space-y-2 text-sm mt-2">
                    <li className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-green-500"></span> <strong>Verde:</strong> Valido (&gt; 60 gg)</li>
                    <li className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-yellow-500"></span> <strong>Giallo:</strong> In Scadenza (≤ 60 gg)</li>
                    <li className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-red-500"></span> <strong>Rosso:</strong> Scaduto</li>
                </ul>
            </GuideCard>
            <GuideCard title="Filtri Temporali" icon={Clock}>
                <p>Usa i pulsanti <strong>3 Mesi</strong>, <strong>6 Mesi</strong> o <strong>1 Anno</strong> in alto a destra per cambiare la scala temporale e vedere più in là nel futuro.</p>
            </GuideCard>
        </div>
      </section>

      <section>
          <h2 className="h2">Funzionalità Chiave</h2>
          <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm">
             <Step number="1" title="Navigazione">
                 <p>Puoi scorrere la timeline orizzontalmente con la rotellina del mouse (o shift + rotella) per muoverti nel tempo.</p>
             </Step>
             <Step number="2" title="Dettagli Rapidi">
                 <p>Passa il mouse sopra una barra colorata per vedere un tooltip con i dettagli esatti: <em>Nome Dipendente, Corso, Data Rilascio e Scadenza precisa.</em></p>
             </Step>
             <Step number="3" title="Esportazione Report">
                 <p>Clicca su <strong>Esporta PDF</strong> <FileText size={14} className="inline"/> per generare un report stampabile di tutte le scadenze visibili, ottimo per le riunioni di direzione.</p>
             </Step>
             <Step number="4" title="Invio Email">
                 <p>Clicca su <strong>Genera Email</strong> <Mail size={14} className="inline"/> per preparare automaticamente una bozza di sollecito per i responsabili, con allegato il report delle scadenze imminenti.</p>
             </Step>
          </div>
      </section>

      <Note type="info" title="Logica di Visualizzazione">
          Per evitare confusione, lo scadenzario mostra di default solo i certificati <strong>In Scadenza</strong> o <strong>Scaduti</strong>. I certificati validi a lungo termine sono nascosti per mantenere la vista pulita, a meno che non cambi i filtri.
      </Note>
    </div>
  );
};

export default CalendarGuide;
