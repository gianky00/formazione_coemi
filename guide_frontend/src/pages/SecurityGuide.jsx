import React from 'react';
import GuideCard from '../components/ui/GuideCard';
import Note from '../components/ui/Note';
import { Lock, Eye, Key, FileWarning, Zap } from 'lucide-react';

const SecurityGuide = () => {
  return (
    <div className="space-y-12">
      <div className="max-w-3xl">
        <h1 className="h1">Sicurezza & Audit</h1>
        <p className="text-body text-xl">
          Proteggi i tuoi dati sensibili. Scopri come Intelleo garantisce l'integrità del database e traccia ogni operazione critica.
        </p>
      </div>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GuideCard title="Crittografia" icon={Lock}>
            <p>Il database <code>database_documenti.db</code> è cifrato su disco (AES-256). Se qualcuno ruba il file, non potrà leggerne il contenuto senza la chiave univoca del software.</p>
        </GuideCard>
        <GuideCard title="In-Memory DB" icon={Zap}>
            <p>Per massima velocità e sicurezza, il database viene decifrato e caricato interamente nella RAM all'avvio. Nessun dato in chiaro viene mai scritto su disco durante l'uso.</p>
        </GuideCard>
        <GuideCard title="Lock File" icon={FileWarning}>
            <p>Un sistema di "Locking" impedisce a due utenti di modificare il database contemporaneamente, prevenendo corruzione dei dati o conflitti di salvataggio.</p>
        </GuideCard>
      </section>

      <section>
          <h2 className="h2 flex items-center gap-2"><Eye className="text-blue-600"/> Audit Log (Registro Attività)</h2>
          <p className="text-body mb-6">
              Per conformità GDPR e sicurezza interna, ogni azione critica viene registrata in un log immutabile.
          </p>

          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm mb-6">
              <table className="w-full text-sm text-left">
                  <thead className="bg-gray-50 text-gray-500 font-semibold uppercase text-xs border-b">
                      <tr>
                          <th className="px-6 py-3">Evento</th>
                          <th className="px-6 py-3">Severità</th>
                          <th className="px-6 py-3">Descrizione</th>
                      </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                      <tr className="hover:bg-gray-50">
                          <td className="px-6 py-3 font-medium">LOGIN_FAILED</td>
                          <td className="px-6 py-3 text-orange-500 font-bold">MEDIUM</td>
                          <td className="px-6 py-3 text-gray-600">Tentativo di accesso fallito (password errata).</td>
                      </tr>
                       <tr className="hover:bg-gray-50">
                          <td className="px-6 py-3 font-medium">CERTIFICATE_DELETED</td>
                          <td className="px-6 py-3 text-red-600 font-bold">HIGH</td>
                          <td className="px-6 py-3 text-gray-600">L'utente Admin ha eliminato il certificato ID #402.</td>
                      </tr>
                       <tr className="hover:bg-gray-50">
                          <td className="px-6 py-3 font-medium">SETTINGS_CHANGED</td>
                          <td className="px-6 py-3 text-blue-600 font-bold">LOW</td>
                          <td className="px-6 py-3 text-gray-600">Modificate impostazioni SMTP (Email).</td>
                      </tr>
                  </tbody>
              </table>
          </div>
          <Note type="info" title="Consultazione">
              Solo gli amministratori possono vedere l'Audit Log completo nella sezione <strong>Configurazione &gt; Log Attività</strong>.
          </Note>
      </section>

      <section>
          <h2 className="h2 flex items-center gap-2"><Key className="text-purple-600"/> Gestione Utenti</h2>
          <div className="space-y-4">
              <GuideCard>
                  <h3 className="font-bold text-gray-900 mb-2">Utente Admin Default</h3>
                  <p className="text-sm text-gray-600">
                      Al primo avvio, il sistema crea un utente <code>admin</code>. Ti verrà chiesto di impostare una password sicura immediatamente.
                  </p>
              </GuideCard>
              <GuideCard>
                  <h3 className="font-bold text-gray-900 mb-2">Creazione Nuovi Utenti</h3>
                  <p className="text-sm text-gray-600">
                      Puoi creare account aggiuntivi per i colleghi. Ogni azione nel log sarà tracciata con lo specifico username di chi l'ha eseguita.
                  </p>
              </GuideCard>
          </div>
      </section>

      <Note type="warning" title="Brute Force Protection">
          Dopo 5 tentativi di login falliti consecutivi, l'account viene temporaneamente bloccato e viene inviata un'email di allerta all'amministratore (se configurata).
      </Note>
    </div>
  );
};

export default SecurityGuide;
