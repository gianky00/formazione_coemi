import React from 'react';
import GuideCard from '../components/ui/GuideCard';
import Note from '../components/ui/Note';
import Step from '../components/ui/Step';
import { Users, FileSpreadsheet, UserPlus, Link } from 'lucide-react';

const EmployeesGuide = () => {
  return (
    <div className="space-y-12">
      <div className="max-w-3xl">
        <h1 className="h1">Gestione Dipendenti</h1>
        <p className="text-body text-xl">
          Gestisci l'anagrafica del personale. Intelleo collega automaticamente i certificati alle persone giuste usando il nome e la matricola.
        </p>
      </div>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
              <h2 className="h2 flex items-center gap-2"><UserPlus className="text-blue-600"/> Importazione Massiva</h2>
              <p className="text-body mb-4">
                  Il modo più veloce per popolare l'anagrafica è importare un file CSV (Excel).
              </p>
              <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                  <h4 className="font-bold text-gray-800 mb-2">Formato Richiesto (.csv)</h4>
                  <div className="code-block bg-gray-50 text-gray-600 border-gray-200 text-xs mb-4">
                      Cognome;Nome;Data_nascita;Badge<br/>
                      ROSSI;MARIO;15/05/1980;101<br/>
                      BIANCHI;LUCA;20/11/1992;102
                  </div>
                  <Step number="1" title="Prepara il File">
                      Usa Excel e salva come "CSV (delimitato dal separatore di elenco)". Assicurati di avere le 4 colonne indicate.
                  </Step>
                  <Step number="2" title="Carica">
                      Vai su <strong>Configurazione &gt; Importa Dipendenti</strong> e seleziona il file.
                  </Step>
              </div>
          </div>

          <div>
               <h2 className="h2 flex items-center gap-2"><Link className="text-purple-600"/> Collegamento Automatico</h2>
               <p className="text-body mb-4">
                   Quando importi un nuovo dipendente, Intelleo fa una magia:
               </p>
               <GuideCard className="border-purple-200 bg-purple-50">
                   <h3 className="font-bold text-purple-900 mb-2">Retro-Scan degli Orfani</h3>
                   <p className="text-purple-800 text-sm">
                       Il sistema scansiona immediatamente tutti i certificati "Orfani" (che non avevano una matricola). Se trova una corrispondenza con il nuovo dipendente (stesso nome + data di nascita), li <strong>collega automaticamente</strong>.
                   </p>
               </GuideCard>
               <div className="mt-6">
                   <Note type="tip" title="Omonimie">
                       Intelleo gestisce i casi di omonimia (es. due "Mario Rossi") usando la <strong>Data di Nascita</strong> come discriminante univoco. Assicurati che sia sempre presente nel CSV.
                   </Note>
               </div>
          </div>
      </section>

      <section>
          <h2 className="h2">Modifica Manuale</h2>
          <p className="text-body">
              Al momento, la modifica dei dati anagrafici (es. correzione nome errato) avviene principalmente tramite il ricaricamento del CSV aggiornato (modalità "Upsert": aggiorna se esiste, crea se nuovo).
          </p>
      </section>
    </div>
  );
};

export default EmployeesGuide;
