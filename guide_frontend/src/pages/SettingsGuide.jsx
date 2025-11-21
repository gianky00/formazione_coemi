import React from 'react';
import { motion } from 'framer-motion';
import { Settings, Mail, Key, Bell } from 'lucide-react';

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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Section title="Server Email (SMTP)">
          <div className="flex items-start gap-3 mb-4">
            <Mail size={20} className="text-blue-500 mt-1 shrink-0" />
            <p>
              Configura il server di posta in uscita per l'invio delle notifiche automatiche.
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded border border-gray-200 text-sm space-y-2">
            <p><strong>Gmail:</strong> smtp.gmail.com (Porta 465, SSL)</p>
            <p><strong>Outlook:</strong> smtp.office365.com (Porta 587, STARTTLS)</p>
            <p><strong>Aruba:</strong> smtps.aruba.it (Porta 465, SSL)</p>
          </div>
          <p className="text-xs text-gray-500 mt-2 italic">
            Nota: Per Gmail è necessario utilizzare una "App Password" invece della password del tuo account.
          </p>
        </Section>

        <Section title="Chiavi API">
          <div className="flex items-start gap-3 mb-4">
            <Key size={20} className="text-yellow-600 mt-1 shrink-0" />
            <p>
              Intelleo utilizza l'Intelligenza Artificiale di Google (Gemini Pro) per l'analisi dei documenti.
            </p>
          </div>
          <p className="text-sm">
            Inserisci qui la tua chiave <code>GOOGLE_API_KEY</code>. Senza una chiave valida, l'importazione automatica dei file non funzionerà.
          </p>
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
    </div>
  );
};

export default SettingsGuide;
