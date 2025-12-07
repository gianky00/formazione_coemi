import React from 'react';
import GuideCard from '../components/ui/GuideCard';
import Note from '../components/ui/Note';
import Step from '../components/ui/Step';
import { Mail, Bell, Monitor } from 'lucide-react';

const SettingsGuide = () => {
  return (
    <div className="space-y-12">
      <div className="max-w-3xl">
        <h1 className="h1">Configurazione</h1>
        <p className="text-body text-xl">
          Personalizza Intelleo per adattarlo alle esigenze della tua azienda. Gestisci notifiche email, soglie di allarme e percorsi di salvataggio.
        </p>
      </div>

      <section>
          <h2 className="h2 flex items-center gap-2"><Mail className="text-blue-600"/> Impostazioni Email (SMTP)</h2>
          <p className="text-body mb-6">
              Per inviare notifiche automatiche di scadenza, Intelleo deve collegarsi al tuo server di posta.
          </p>

          <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm">
             <div className="flex gap-4 mb-6">
                 <div className="flex-1">
                     <label htmlFor="preset-select" className="block text-sm font-medium text-gray-700 mb-1">Preset Rapidi</label>
                     <select id="preset-select" className="w-full border-gray-300 rounded-md shadow-sm bg-gray-50 p-2 text-sm" disabled>
                         <option>Gmail (OAuth/App Password)</option>
                         <option>Outlook / Office 365</option>
                         <option>Aruba (SMTPS)</option>
                         <option>Personalizzato...</option>
                     </select>
                     <p className="text-xs text-gray-500 mt-1">Scegli il tuo provider per compilare automaticamente porte e indirizzi.</p>
                 </div>
             </div>

             <Step number="1" title="Server & Porta">
                 <p>Solitamente <code>smtp.gmail.com</code> (Porta 465 SSL) o <code>smtps.aruba.it</code>. Il sistema tenta automaticamente SSL o STARTTLS.</p>
             </Step>
             <Step number="2" title="Autenticazione">
                 <p>Inserisci l'email mittente e la password. <strong>Nota per Gmail:</strong> Devi usare una "Password per le App" (App Password) generata dal tuo account Google, non la tua password di login normale.</p>
             </Step>
             <Step number="3" title="Test Connessione">
                 <p>Clicca sempre su "Test Email" prima di salvare. Riceverai una mail di prova se tutto funziona.</p>
             </Step>
          </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
          <div>
              <h2 className="h2 flex items-center gap-2"><Bell className="text-orange-500"/> Soglie di Allarme</h2>
              <GuideCard className="h-full">
                  <p className="mb-4">Decidi con quanto anticipo vuoi essere avvisato delle scadenze.</p>
                  <ul className="space-y-4">
                      <li className="flex justify-between items-center border-b pb-2">
                          <span>Soglia Standard</span>
                          <span className="font-mono bg-gray-100 px-2 rounded">60 Giorni</span>
                      </li>
                      <li className="flex justify-between items-center border-b pb-2">
                          <span>Soglia Visite Mediche</span>
                          <span className="font-mono bg-gray-100 px-2 rounded">30 Giorni</span>
                      </li>
                  </ul>
                  <p className="text-xs text-gray-500 mt-4">
                      I certificati diventano "Gialli" (In Scadenza) quando mancano meno giorni di quelli indicati qui.
                  </p>
              </GuideCard>
          </div>

          <div>
               <h2 className="h2 flex items-center gap-2"><Monitor className="text-purple-600"/> Percorsi & Sistema</h2>
               <GuideCard className="h-full">
                   <p className="mb-4">Gestisci dove Intelleo salva i suoi dati.</p>
                   <Step number="A" title="Database Path">
                       <p>Puoi spostare l'intera cartella dei documenti su un percorso di rete (es. <code>Z:\Sicurezza\Intelleo</code>) per renderla accessibile ai backup server aziendali.</p>
                   </Step>
                   <Step number="B" title="Licenza">
                       <p>Qui vedi lo stato della tua licenza, la data di scadenza e l'Hardware ID necessario per i rinnovi.</p>
                   </Step>
               </GuideCard>
          </div>
      </section>

      <Note type="warning" title="Permessi di Scrittura">
          Se cambi il percorso del database su una cartella di rete, assicurati che l'utente Windows abbia permessi di <strong>Lettura e Scrittura</strong> completi su quella cartella.
      </Note>
    </div>
  );
};

export default SettingsGuide;
