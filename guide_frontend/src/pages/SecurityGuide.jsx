import React from 'react';
import { Shield, AlertTriangle, Eye, Activity, Smartphone, Mail, Database, Lock, CheckCircle } from 'lucide-react';
import AuditSimulator from '../components/AuditSimulator';
import { motion } from 'framer-motion';

const Section = ({ title, icon: Icon, children }) => (
  <section className="mb-12">
    <h2 className="text-2xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2 flex items-center gap-2">
      {Icon && <Icon className="text-blue-600" size={24} />}
      {title}
    </h2>
    <div className="text-gray-600 leading-relaxed space-y-4">
      {children}
    </div>
  </section>
);

const SecurityGuide = () => {
  return (
    <div className="max-w-4xl mx-auto">
       {/* Header */}
       <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-blue-100 rounded-lg text-blue-700">
            <Shield size={24} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Sicurezza & Audit</h1>
        </div>
        <p className="text-lg text-gray-500 ml-14">
          Protezione dei dati di livello bancario e tracciamento completo di ogni operazione.
        </p>
      </motion.div>

      {/* Interactive Simulator */}
      <Section title="Log Attività Interattivo" icon={Activity}>
        <p className="mb-4">
          Il <strong>Log Attività</strong> è la "scatola nera" di Intelleo. Registra tutto ciò che accade.
          <br/>
          <span className="text-sm text-blue-600 font-medium bg-blue-50 px-2 py-1 rounded">
            Prova tu stesso: Clicca su una riga per vedere i dettagli nascosti o usa i filtri per cercare eventi specifici.
          </span>
        </p>
        <AuditSimulator />
      </Section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
        {/* Indicatori Visivi */}
        <Section title="Livelli di Allerta" icon={Eye}>
             <p className="text-sm mb-4">Il sistema classifica ogni evento con un colore per aiutarti a capire subito la gravità.</p>
             <div className="space-y-3">
                <div className="bg-white p-3 rounded-lg border-l-4 border-green-500 shadow-sm">
                  <h3 className="font-bold text-gray-800 text-sm">LOW (Verde)</h3>
                  <p className="text-xs text-gray-600">Tutto ok. Operazioni di routine (es. Login, Salvataggio dati).</p>
                </div>
                <div className="bg-orange-50 p-3 rounded-lg border-l-4 border-orange-500 shadow-sm">
                  <h3 className="font-bold text-orange-800 text-sm">MEDIUM (Arancione)</h3>
                  <p className="text-xs text-orange-700">Attenzione. Qualcosa di inusuale (es. Modifica impostazioni email).</p>
                </div>
                <div className="bg-red-50 p-3 rounded-lg border-l-4 border-red-500 shadow-sm">
                  <h3 className="font-bold text-red-800 text-sm">CRITICAL (Rosso)</h3>
                  <p className="text-xs text-red-700">Pericolo. Attacco in corso o violazione (es. Password errata 5 volte).</p>
                </div>
             </div>
        </Section>

        {/* Database Protection */}
        <Section title="Protezione Database" icon={Database}>
             <p className="text-sm mb-4">I tuoi dati sono al sicuro, anche se qualcuno dovesse rubare il file dal computer.</p>
            <div className="space-y-4">
                <div className="flex items-start gap-3">
                    <Shield className="w-5 h-5 text-green-600 mt-1 shrink-0" />
                    <div>
                        <strong className="text-gray-900 text-sm">Crittografia AES-256</strong>
                        <p className="text-xs text-gray-600">Il database è cifrato su disco. Senza la chiave interna del programma, è illeggibile.</p>
                    </div>
                </div>
                <div className="flex items-start gap-3">
                    <Lock className="w-5 h-5 text-purple-600 mt-1 shrink-0" />
                    <div>
                        <strong className="text-gray-900 text-sm">Blocco Anti-Corruzione</strong>
                        <p className="text-xs text-gray-600">Un file speciale (<code>.lock</code>) impedisce a due persone di scrivere contemporaneamente, evitando errori.</p>
                    </div>
                </div>
                 <div className="flex items-start gap-3">
                    <Smartphone className="w-5 h-5 text-blue-600 mt-1 shrink-0" />
                    <div>
                        <strong className="text-gray-900 text-sm">Impronta Dispositivo</strong>
                        <p className="text-xs text-gray-600">Ogni PC ha un "Device ID". Se un utente accede da un computer sconosciuto, lo saprai.</p>
                    </div>
                </div>
            </div>
        </Section>
      </div>

      {/* Notifications */}
      <div className="mt-8 bg-blue-50 border border-blue-100 rounded-xl p-6">
          <h3 className="text-lg font-bold text-blue-900 mb-2 flex items-center gap-2">
              <Mail size={20} /> Reazione Automatica
          </h3>
          <p className="text-blue-800 text-sm leading-relaxed">
              Non devi controllare il Log ogni giorno. Se succede qualcosa di <strong>CRITICO</strong> (es. qualcuno tenta di indovinare la password dell'amministratore), Intelleo ti invia immediatamente una <strong>email di allerta</strong> con tutti i dettagli (IP, Orario e Utente).
          </p>
      </div>

    </div>
  );
};

export default SecurityGuide;
