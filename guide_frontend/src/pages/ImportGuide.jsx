import React from 'react';
import { motion } from 'framer-motion';
import { FileText, UploadCloud, FolderOpen, Cpu, CheckCircle, AlertTriangle } from 'lucide-react';

const Section = ({ title, children }) => (
  <section className="mb-12">
    <h2 className="text-2xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">{title}</h2>
    <div className="text-gray-600 leading-relaxed space-y-4">
      {children}
    </div>
  </section>
);

const ImportGuide = () => {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-purple-100 rounded-lg text-purple-700">
            <FileText size={24} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Importazione & AI</h1>
        </div>
        <p className="text-lg text-gray-500 ml-14">
          Automatizza l'inserimento dati grazie all'Intelligenza Artificiale. Trascina, analizza e organizza i tuoi documenti in pochi secondi.
        </p>
      </motion.div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

        <Section title="Come Funziona">
          <p>
            Intelleo utilizza un motore AI avanzato (Gemini Pro) per leggere il contenuto dei tuoi PDF come farebbe un umano. Non si basa su template fissi, ma "capisce" il documento.
          </p>
          <ul className="space-y-3 mt-4">
            <li className="flex items-start gap-3">
              <UploadCloud size={20} className="text-blue-500 mt-1 shrink-0" />
              <span>
                <strong>Drag & Drop:</strong> Trascina intere cartelle o singoli file nell'area di importazione.
              </span>
            </li>
            <li className="flex items-start gap-3">
              <Cpu size={20} className="text-purple-500 mt-1 shrink-0" />
              <span>
                <strong>Analisi AI:</strong> Il sistema estrae automaticamente il nome del dipendente, il corso, la data di rilascio e la scadenza.
              </span>
            </li>
            <li className="flex items-start gap-3">
              <FolderOpen size={20} className="text-orange-500 mt-1 shrink-0" />
              <span>
                <strong>Organizzazione Automatica:</strong> I file vengono rinominati e spostati nella cartella <code>DOCUMENTI DIPENDENTI</code>.
              </span>
            </li>
          </ul>
        </Section>

        <Section title="Integrazione Windows">
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <h3 className="font-bold text-gray-800 mb-2">Tasto Destro del Mouse</h3>
            <p className="text-sm mb-3">
              Puoi avviare l'analisi direttamente da Windows senza aprire prima l'applicazione.
            </p>
            <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
              <li>Fai click destro su una cartella contenente PDF.</li>
              <li>Seleziona la voce <strong>"Analizza con Intelleo"</strong>.</li>
              <li>L'applicazione si aprirà e inizierà immediatamente l'elaborazione.</li>
            </ol>
          </div>
        </Section>
      </div>

      <Section title="Regole di Rinomina">
        <p className="mb-4">
          Per garantire un archivio ordinato, Intelleo rinomina i file analizzati seguendo uno standard rigoroso:
        </p>
        <div className="bg-slate-800 text-slate-200 p-4 rounded-md font-mono text-sm overflow-x-auto">
          COGNOME NOME (MATRICOLA) - CATEGORIA - DD_MM_YYYY.pdf
        </div>
        <p className="mt-4 text-sm text-gray-500">
          <em>Esempio:</em> <code>ROSSI MARIO (12345) - ANTINCENDIO - 15_06_2026.pdf</code>
        </p>
        <div className="mt-4 flex items-start gap-3 bg-blue-50 p-3 rounded text-sm text-blue-800">
          <AlertTriangle size={16} className="mt-1 shrink-0" />
          <p>
            Se la matricola non viene trovata, verrà usato "N-A". Se la data di scadenza non è presente, verrà usato "no scadenza".
          </p>
        </div>
      </Section>
    </div>
  );
};

export default ImportGuide;
