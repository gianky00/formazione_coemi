import React from 'react';
import { motion } from 'framer-motion';
import { HardDrive, Save, RefreshCw, AlertTriangle, FileCode } from 'lucide-react';

const Section = ({ title, children }) => (
  <section className="mb-12">
    <h2 className="text-2xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">{title}</h2>
    <div className="text-gray-600 leading-relaxed space-y-4">
      {children}
    </div>
  </section>
);

const MaintenanceGuide = () => {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-emerald-100 rounded-lg text-emerald-700">
            <HardDrive size={24} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Backup & Manutenzione</h1>
        </div>
        <p className="text-lg text-gray-500 ml-14">
          Procedure essenziali per proteggere i tuoi dati e migrare l'applicazione su nuovi dispositivi.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 gap-8">

        <Section title="Dove sono i miei dati?">
          <p>
            Per garantire la sicurezza e la compatibilità con Windows, Intelleo non salva nulla nella cartella di installazione (Program Files).
            Tutti i dati risiedono nella cartella sicura dell'utente corrente.
          </p>
          <div className="bg-slate-800 text-slate-200 p-4 rounded-md font-mono text-sm overflow-x-auto mt-2">
            %LOCALAPPDATA%\Intelleo
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Tipicamente il percorso completo è: <code>C:\Users\TUO_NOME_UTENTE\AppData\Local\Intelleo</code>
          </p>
        </Section>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <Section title="File da Salvare">
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="bg-blue-100 p-2 rounded text-blue-700 mt-1">
                    <HardDrive size={20} />
                  </div>
                  <div>
                    <strong className="text-gray-800">database_documenti.db</strong>
                    <p className="text-sm">Contiene tutti i dati: dipendenti, certificati, storico e log. È criptato e non può essere aperto con programmi esterni.</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="bg-yellow-100 p-2 rounded text-yellow-700 mt-1">
                    <FileCode size={20} />
                  </div>
                  <div>
                    <strong className="text-gray-800">.env</strong>
                    <p className="text-sm">Contiene la configurazione: parametri email, chiavi API e impostazioni personalizzate.</p>
                  </div>
                </li>
              </ul>
            </Section>

            <Section title="Procedura di Backup">
              <div className="bg-emerald-50 border border-emerald-100 p-4 rounded-lg">
                <h3 className="font-bold text-emerald-800 mb-2 flex items-center gap-2">
                    <Save size={18} /> Backup Manuale
                </h3>
                <ol className="list-decimal list-inside space-y-2 text-sm text-emerald-900">
                  <li>Chiudi completamente Intelleo.</li>
                  <li>Apri <strong>Esplora Risorse</strong>.</li>
                  <li>Digita <code>%LOCALAPPDATA%\Intelleo</code> nella barra degli indirizzi e premi Invio.</li>
                  <li>Copia i file <code>database_documenti.db</code> e <code>.env</code>.</li>
                  <li>Incollali in un luogo sicuro (es. Hard Disk esterno, Cloud aziendale).</li>
                </ol>
              </div>
            </Section>
        </div>

        <Section title="Ripristino & Migrazione">
          <p className="mb-4">
            Per ripristinare i dati dopo un incidente o per spostare Intelleo su un nuovo PC, segui questi passaggi:
          </p>

          <div className="space-y-4">
            <div className="flex items-start gap-3 bg-white border border-gray-200 p-4 rounded-lg">
                <div className="bg-gray-100 text-gray-600 w-6 h-6 flex items-center justify-center rounded-full font-bold text-xs shrink-0 mt-0.5">1</div>
                <div>
                    <h4 className="font-bold text-gray-800">Installa Intelleo</h4>
                    <p className="text-sm text-gray-600">Esegui l'installazione pulita sul nuovo PC e avvia il programma almeno una volta (per creare le cartelle), poi chiudilo.</p>
                </div>
            </div>

            <div className="flex items-start gap-3 bg-white border border-gray-200 p-4 rounded-lg">
                <div className="bg-gray-100 text-gray-600 w-6 h-6 flex items-center justify-center rounded-full font-bold text-xs shrink-0 mt-0.5">2</div>
                <div>
                    <h4 className="font-bold text-gray-800">Sostituisci i File</h4>
                    <p className="text-sm text-gray-600">Vai nella cartella <code>%LOCALAPPDATA%\Intelleo</code> del nuovo PC e incolla i file del backup, sovrascrivendo quelli esistenti.</p>
                </div>
            </div>

            <div className="flex items-start gap-3 bg-white border border-gray-200 p-4 rounded-lg">
                <div className="bg-gray-100 text-gray-600 w-6 h-6 flex items-center justify-center rounded-full font-bold text-xs shrink-0 mt-0.5">3</div>
                <div>
                    <h4 className="font-bold text-gray-800">Riavvia</h4>
                    <p className="text-sm text-gray-600">Apri Intelleo. Ritroverai tutti i tuoi dati, la configurazione e lo storico esattamente come li avevi lasciati.</p>
                </div>
            </div>
          </div>

          <div className="mt-6 flex items-start gap-3 bg-amber-50 p-4 rounded text-sm text-amber-800 border border-amber-100">
            <AlertTriangle size={20} className="mt-1 shrink-0" />
            <p>
              <strong>Attenzione:</strong> Non tentare di aprire il file database con Excel o Access. Rischieresti di corrompere i dati in modo irreversibile. Usa sempre la procedura di ripristino descritta qui.
            </p>
          </div>
        </Section>

      </div>
    </div>
  );
};

export default MaintenanceGuide;
