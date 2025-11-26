import React from 'react';
import { motion } from 'framer-motion';
import { Settings, Mail, Key, Bell, Users, Activity } from 'lucide-react';

const Section = ({ title, children }) => (
  <section className="mb-12">
    <h2 className="text-2xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">{title}</h2>
    <div className="text-gray-600 leading-relaxed space-y-4">
      {children}
    </div>
  </section>
);

const SettingsGuide = () => {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-gray-200 rounded-lg text-gray-700">
            <Settings size={24} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Configurazione</h1>
        </div>
        <p className="text-lg text-gray-500 ml-14">
          Personalizza il comportamento dell'applicazione, gestisci le credenziali e le preferenze di notifica.
        </p>
      </motion.div>

      <Section title="Navigazione">
        <p>
          La sezione Configurazione è organizzata in tre schede principali, accessibili solo agli amministratori:
        </p>
        <ul className="list-disc list-inside mt-2 space-y-1">
          <li><strong>Parametri Generali:</strong> Per impostazioni di base, API e percorsi.</li>
          <li><strong>Account:</strong> Per la gestione degli utenti.</li>
          <li><strong>Log Attività:</strong> Per il monitoraggio della sicurezza.</li>
        </ul>
      </Section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Section title="Gestione Account (Admin)">
           <div className="flex items-start gap-3 mb-4">
             <Users size={20} className="text-indigo-600 mt-1 shrink-0" />
             <p>
               Da qui gli amministratori possono creare nuovi account per i colleghi e gestire i permessi.
             </p>
           </div>
           <div className="bg-indigo-50 p-4 rounded border border-indigo-100 text-sm">
             <p className="mb-2"><strong>Funzionalità disponibili:</strong></p>
             <ul className="list-disc list-inside space-y-1 text-indigo-900">
               <li>Creazione nuovi utenti.</li>
               <li><strong>Reset password:</strong> Il campo password mostrerà "Lascia vuoto per mantenere la password attuale".</li>
               <li>Assegnazione ruolo Amministratore.</li>
               <li>Eliminazione account (non è possibile eliminare il proprio).</li>
             </ul>
           </div>
        </Section>

        <Section title="Parametri Generali">
           <div className="space-y-4">
             <div className="p-4 border rounded-lg bg-gray-50">
               <h3 className="font-bold text-gray-800 mb-2">Percorso Database</h3>
               <p className="text-sm text-gray-600">
                 Da qui puoi visualizzare e modificare la cartella in cui è salvato il file del database.
                 <br />
                 <span className="font-medium text-red-600">Attenzione:</span> la modifica è consigliata solo a utenti esperti.
               </p>
             </div>
             <div className="p-4 border rounded-lg bg-gray-50">
               <h3 className="font-bold text-gray-800 mb-2">Destinatari Notifiche</h3>
               <p className="text-sm text-gray-600">
                 Inserisci gli indirizzi email che riceveranno i report automatici delle scadenze. Puoi specificare destinatari principali (To) e in copia conoscenza (CC), separandoli con una virgola.
               </p>
             </div>
           </div>
        </Section>

        <Section title="Server Email (SMTP)">
          <div className="flex items-start gap-3 mb-4">
            <Mail size={20} className="text-blue-500 mt-1 shrink-0" />
            <p>
              Configura il server di posta in uscita per l'invio delle notifiche.
            </p>
          </div>
          <div className="bg-blue-50 p-4 rounded border border-blue-100 mb-4">
            <h3 className="font-bold text-blue-900 mb-2">Preset Rapidi</h3>
            <p className="text-sm text-blue-800">
              Utilizza il menu a tendina <strong>"Preset Email"</strong> per configurare automaticamente i parametri più comuni:
            </p>
            <ul className="list-disc list-inside mt-2 text-sm text-blue-800 font-medium">
              <li>Gmail (Richiede App Password)</li>
              <li>Outlook / Office 365</li>
              <li>COEMI (Server Aziendale)</li>
            </ul>
          </div>
          <div className="bg-gray-50 p-4 rounded border border-gray-200 text-sm space-y-2">
            <p><strong>Gmail:</strong> smtp.gmail.com (Porta 465, SSL)</p>
            <p><strong>Outlook:</strong> smtp.office365.com (Porta 587, STARTTLS)</p>
            <p><strong>Aruba:</strong> smtps.aruba.it (Porta 465, SSL)</p>
          </div>
        </Section>

        <Section title="Configurazione Google Cloud API">
          <div className="flex items-start gap-3 mb-4">
            <Key size={20} className="text-yellow-600 mt-1 shrink-0" />
            <p>
              Per abilitare l'intelligenza artificiale, è necessario generare una chiave API personale su Google Cloud.
            </p>
          </div>

          <div className="space-y-4 text-sm">
            <div className="flex gap-3">
              <div className="bg-gray-100 text-gray-600 w-6 h-6 flex items-center justify-center rounded-full font-bold text-xs shrink-0">1</div>
              <p>Accedi alla <a href="https://console.cloud.google.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google Cloud Console</a> con il tuo account aziendale.</p>
            </div>

            <div className="flex gap-3">
              <div className="bg-gray-100 text-gray-600 w-6 h-6 flex items-center justify-center rounded-full font-bold text-xs shrink-0">2</div>
              <div>
                <p>Crea un <strong>Nuovo Progetto</strong> e dagli un nome (es. "Intelleo-AI").</p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="bg-gray-100 text-gray-600 w-6 h-6 flex items-center justify-center rounded-full font-bold text-xs shrink-0">3</div>
              <div>
                <p>Nella barra di ricerca in alto, digita <strong>"Generative AI API"</strong> (o "Vertex AI API") e abilitala.</p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="bg-gray-100 text-gray-600 w-6 h-6 flex items-center justify-center rounded-full font-bold text-xs shrink-0">4</div>
              <div>
                <p>Vai su <strong>APIs & Services {'>'} Credentials</strong>.</p>
                <p>Clicca su <strong>Create Credentials</strong> e seleziona <strong>API Key</strong>.</p>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="bg-gray-100 text-gray-600 w-6 h-6 flex items-center justify-center rounded-full font-bold text-xs shrink-0">5</div>
              <div>
                <p>Copia la stringa generata (inizia con <code>AIza...</code>) e incollala nel campo <strong>Gemini API Key</strong> di Intelleo.</p>
              </div>
            </div>
          </div>
        </Section>
      </div>

      <Section title="Notifiche e Scadenze">
        <div className="flex items-start gap-3">
          <Bell size={20} className="text-red-500 mt-1 shrink-0" />
          <div>
            <h3 className="font-bold text-gray-800 mb-2">Soglie di Avviso</h3>
            <p className="mb-2">
              Definisci con quanto anticipo vuoi essere avvisato delle scadenze.
            </p>
            <ul className="list-disc list-inside text-sm space-y-1 text-gray-600">
              <li><strong>Generale:</strong> Default 60 giorni.</li>
              <li><strong>Visite Mediche:</strong> Default 30 giorni.</li>
            </ul>
          </div>
        </div>
      </Section>

        <Section title="Log Attività">
           <div className="flex items-start gap-3">
             <Activity size={20} className="text-blue-600 mt-1 shrink-0" />
             <div>
               <h3 className="font-bold text-gray-800 mb-2">Sicurezza e Audit</h3>
               <p className="text-sm text-gray-600">
                 La scheda "Log Attività" permette di monitorare tutte le operazioni sensibili.
                 Per maggiori dettagli, consulta la guida dedicata <strong className="text-blue-600">Sicurezza & Audit</strong>.
               </p>
             </div>
           </div>
        </Section>
    </div>
  );
};

export default SettingsGuide;
