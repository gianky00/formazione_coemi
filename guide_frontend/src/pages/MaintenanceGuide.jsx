import React from 'react';
import GuideCard from '../components/ui/GuideCard';
import Note from '../components/ui/Note';
import Step from '../components/ui/Step';
import { Archive, HardDrive, RefreshCw } from 'lucide-react';

const MaintenanceGuide = () => {
  return (
    <div className="space-y-12">
      <div className="max-w-3xl">
        <h1 className="h1">Backup & Manutenzione</h1>
        <p className="text-body text-xl">
          Proteggi il tuo lavoro. Impara a fare copie di sicurezza e a migrare Intelleo su un nuovo computer senza perdere dati.
        </p>
      </div>

      <section>
          <h2 className="h2 flex items-center gap-2"><Archive className="text-blue-600"/> Backup Manuale</h2>
          <p className="text-body mb-6">
              Non esiste un pulsante "Backup" unico, perché Intelleo è basato su file. Per salvare tutto, devi copiare la cartella dati.
          </p>

          <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm">
             <Step number="1" title="Localizza la Cartella Dati">
                 <p>Apri <strong>Configurazione</strong> e guarda il percorso indicato sotto "Database Path". Di solito è <code>%LOCALAPPDATA%\Intelleo</code>.</p>
             </Step>
             <Step number="2" title="Chiudi Intelleo">
                 <p>Assicurati che il programma sia completamente chiuso (controlla che non ci sia il file <code>.lock</code> nella cartella).</p>
             </Step>
             <Step number="3" title="Copia-Incolla">
                 <p>Copia l'intera cartella <code>Intelleo</code> su una chiavetta USB o un disco esterno.</p>
             </Step>
          </div>
          <Note type="tip" title="Cosa stai salvando?">
              Copiando quella cartella salvi: il Database cifrato, tutti i PDF organizzati, il file di configurazione (settings.json) e la Licenza.
          </Note>
      </section>

      <section className="mt-12">
          <h2 className="h2 flex items-center gap-2"><RefreshCw className="text-green-600"/> Migrazione su Nuovo PC</h2>
          <p className="text-body mb-4">
              Hai cambiato computer? Ecco come spostare tutto.
          </p>
          <GuideCard>
              <ul className="space-y-4 text-sm text-gray-700">
                  <li className="flex gap-3">
                      <span className="font-bold text-gray-900 shrink-0">1.</span>
                      <span>Installa Intelleo sul nuovo PC scaricando l'ultimo setup.</span>
                  </li>
                  <li className="flex gap-3">
                      <span className="font-bold text-gray-900 shrink-0">2.</span>
                      <span>Avvia il programma una volta per fargli creare le cartelle iniziali, poi chiudilo.</span>
                  </li>
                  <li className="flex gap-3">
                      <span className="font-bold text-gray-900 shrink-0">3.</span>
                      <span>Sovrascrivi la cartella <code>%LOCALAPPDATA%\Intelleo</code> del nuovo PC con quella che hai salvato dal vecchio PC.</span>
                  </li>
                  <li className="flex gap-3">
                      <span className="font-bold text-gray-900 shrink-0">4.</span>
                      <span>Riavvia Intelleo. Ritroverai tutto esattamente come lo avevi lasciato.</span>
                  </li>
              </ul>
          </GuideCard>

          <div className="mt-6">
            <Note type="warning" title="Attenzione alla Licenza">
                La licenza è legata all'Hardware ID. Spostando i file su un nuovo PC, la licenza risulterà invalida. Dovrai contattare il supporto per far resettare il tuo Hardware ID e attivarla sul nuovo computer.
            </Note>
          </div>
      </section>
    </div>
  );
};

export default MaintenanceGuide;
