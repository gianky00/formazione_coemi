import React from 'react';
import GuideCard from '../components/ui/GuideCard';
import Note from '../components/ui/Note';
import Step from '../components/ui/Step';
import ImportSimulator from '../components/ImportSimulator';
import { UploadCloud, FolderOpen, AlertTriangle } from 'lucide-react';

const ImportGuide = () => {
  return (
    <div className="space-y-12">
      {/* Header */}
      <div className="max-w-3xl">
        <h1 className="h1">Importazione & AI</h1>
        <p className="text-body text-xl">
          Automatizza l'inserimento dati. Trascina i tuoi file e lascia che l'intelligenza artificiale faccia il lavoro pesante.
        </p>
      </div>

      {/* Simulator */}
      <section>
         <h2 className="h2 flex items-center gap-2">
            <UploadCloud className="text-blue-600" />
            Simulazione Processo
        </h2>
        <p className="text-body mb-6">
            Clicca sul box qui sotto per vedere come il sistema analizza i file in tempo reale e li organizza.
        </p>
        <ImportSimulator />
      </section>

      {/* Logic Explanation */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12">
        <GuideCard title="Drag & Drop Intelligente" icon={FolderOpen}>
            <p className="mb-4">
                Non serve dividere i file prima. Puoi trascinare:
            </p>
             <ul className="list-disc pl-5 space-y-2 text-sm text-gray-600">
                <li>Singoli PDF</li>
                <li>Intere cartelle (anche con sottocartelle)</li>
                <li>File misti di diversi dipendenti</li>
            </ul>
        </GuideCard>

        <GuideCard title="Rinominazione Automatica" icon={FileText}>
            <p className="mb-4">
                Se l'analisi ha successo, il file viene rinominato secondo lo standard aziendale:
            </p>
            <div className="code-block bg-gray-100 text-gray-800 border-gray-200 text-xs">
                COGNOME NOME (MATRICOLA) - CATEGORIA - SCADENZA.pdf
            </div>
            <p className="mt-4 text-sm text-gray-500">
                Es: <code>ROSSI MARIO (123) - PLE - 2028-05-15.pdf</code>
            </p>
        </GuideCard>
      </section>

      {/* Outcomes */}
      <section>
        <h2 className="h2">Gestione degli Errori</h2>
        <div className="space-y-4">
            <Note type="success" title="Successo">
                Il file viene spostato in <code>DOCUMENTI DIPENDENTI</code> e il record viene creato nel database.
            </Note>
            <Note type="warning" title="Orfano (Dati Parziali)">
                Se l'AI legge i dati ma non trova la matricola, il file va in <code>DOCUMENTI ANALIZZATI ASSENZA MATRICOLE</code>. Dovrai collegarlo manualmente in "Convalida Dati".
            </Note>
             <Note type="error" title="Errore">
                Se il file è illeggibile o corrotto, finisce in <code>DOCUMENTI NON ANALIZZATI</code>.
            </Note>
        </div>
      </section>

      <section>
          <h2 className="h2">Categorie Supportate</h2>
          <p className="text-body mb-4">L'AI è addestrata per riconoscere specificamente questi documenti:</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
             {['Antincendio', 'Primo Soccorso', 'PLE', 'Gru', 'Atex', 'Preposto', 'BLSD', 'Nomina', 'Medico Competente', 'HLO', 'Tessera HLO', 'Unilav', 'Patente'].map(c => (
                 <div key={c} className="bg-white border border-gray-200 rounded-md px-3 py-2 text-sm font-medium text-gray-700 text-center shadow-sm">
                     {c}
                 </div>
             ))}
          </div>
      </section>

    </div>
  );
};

import { FileText } from 'lucide-react'; // Fix missing import for icon used in GuideCard
export default ImportGuide;
