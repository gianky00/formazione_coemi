import React from 'react';
import { Shield, AlertTriangle, Eye, Activity, Smartphone, Mail } from 'lucide-react';

const SecurityGuide = () => {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6 flex items-center gap-3">
        <Shield className="w-8 h-8 text-blue-700" />
        Sicurezza & Audit
      </h1>

      <div className="space-y-8">
        {/* Intro */}
        <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <p className="text-gray-600 leading-relaxed">
            Il modulo Sicurezza di Intelleo offre un sistema completo di monitoraggio e auditing per proteggere i dati sensibili e tracciare le attività degli utenti.
            Tutte le operazioni critiche vengono registrate in modo immutabile nel <strong>Log Attività</strong>.
          </p>
        </section>

        {/* Log Attività */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            Log Attività (Audit Trail)
          </h2>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 space-y-4">
            <p className="text-gray-600">
              La tabella Log Attività (in <em>Configurazione {'>'} Log Attività</em>) mostra cronologicamente tutte le azioni rilevanti.
            </p>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm text-left text-gray-500">
                <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                  <tr>
                    <th className="px-4 py-2">Colonna</th>
                    <th className="px-4 py-2">Descrizione</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="bg-white border-b">
                    <td className="px-4 py-2 font-medium text-gray-900">Severità</td>
                    <td className="px-4 py-2">Livello di rischio dell'evento (Low, Medium, Critical).</td>
                  </tr>
                  <tr className="bg-white border-b">
                    <td className="px-4 py-2 font-medium text-gray-900">IP & Geo</td>
                    <td className="px-4 py-2">Indirizzo IP di origine e localizzazione approssimativa.</td>
                  </tr>
                  <tr className="bg-white border-b">
                    <td className="px-4 py-2 font-medium text-gray-900">Device ID</td>
                    <td className="px-4 py-2">Impronta digitale univoca del dispositivo (Hardware ID).</td>
                  </tr>
                  <tr className="bg-white border-b">
                    <td className="px-4 py-2 font-medium text-gray-900">Modifiche</td>
                    <td className="px-4 py-2">Dettaglio dei valori cambiati (es. <em>Soglia: 60 {'->'} 30</em>).</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Indicatori Visivi */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Eye className="w-5 h-5 text-blue-600" />
            Indicatori Visivi & Severità
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border-l-4 border-green-500 shadow-sm">
              <h3 className="font-bold text-gray-800 mb-1">LOW (Basso)</h3>
              <p className="text-sm text-gray-600">Attività normali (Login successo, Aggiornamento dati).</p>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg border-l-4 border-orange-500 shadow-sm">
              <h3 className="font-bold text-orange-800 mb-1">MEDIUM (Medio)</h3>
              <p className="text-sm text-orange-700">Eventi sospetti (es. Login fallito, Modifica configurazione sensibile).</p>
            </div>
            <div className="bg-red-50 p-4 rounded-lg border-l-4 border-red-500 shadow-sm">
              <h3 className="font-bold text-red-800 mb-1">CRITICAL (Critico)</h3>
              <p className="text-sm text-red-700">Minacce attive (es. Brute Force Attack, Accesso Admin non autorizzato).</p>
            </div>
          </div>
        </section>

        {/* Protezione Avanzata */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5 text-blue-600" />
            Protezione Avanzata
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="font-bold text-gray-800 mb-2 flex items-center gap-2">
                    <Smartphone className="w-4 h-4 text-blue-500" /> Device Fingerprinting
                </h3>
                <p className="text-sm text-gray-600">
                    Il sistema identifica ogni dispositivo tramite un <strong>Device ID</strong> univoco (basato sulla licenza o sull'hardware).
                    Se un utente accede da una postazione sconosciuta, l'evento viene tracciato.
                </p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="font-bold text-gray-800 mb-2 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-500" /> Rilevamento Anomalie
                </h3>
                <p className="text-sm text-gray-600">
                    Tentativi ripetuti di accesso falliti (Brute Force) o tentativi di accesso a funzioni Admin da parte di utenti non autorizzati
                    vengono bloccati e segnalati come CRITICI.
                </p>
            </div>
          </div>
        </section>

        {/* Notifiche */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Mail className="w-5 h-5 text-blue-600" />
            Notifiche di Sicurezza
          </h2>
          <div className="bg-blue-50 p-6 rounded-xl border border-blue-100 text-blue-900">
            <p>
                Quando viene rilevato un evento di gravità <strong>CRITICAL</strong>, il sistema invia automaticamente una
                <strong>email di allerta immediata</strong> agli amministratori configurati, contenente i dettagli dell'attacco (IP, Utente, Tipo di azione).
            </p>
          </div>
        </section>
      </div>
    </div>
  );
};

export default SecurityGuide;
