import React from 'react';
import { Shield, AlertTriangle, Eye, Activity, Smartphone, Mail, Database, Lock } from 'lucide-react';

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

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 space-y-6">
            <div>
              <h3 className="text-md font-bold text-gray-800 mb-2">Navigazione e Filtri</h3>
              <p className="text-gray-600 mb-3 text-sm">
                Per investigare su eventi specifici, utilizza la barra degli strumenti sopra la tabella:
              </p>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1 ml-2">
                <li><strong>Utente:</strong> Filtra le azioni compiute da uno specifico account.</li>
                <li><strong>Categoria:</strong> Isola il tipo di evento (es. <em>AUTH</em> per i login, <em>CERTIFICATE</em> per i dati).</li>
                <li><strong>Intervallo Date:</strong> Seleziona una data di inizio e fine per restringere la ricerca temporale.</li>
              </ul>
              <div className="mt-2 text-xs bg-gray-100 p-2 rounded text-gray-500">
                Clicca su <strong>"Aggiorna"</strong> dopo aver modificato i filtri per ricaricare i dati.
              </div>
            </div>

            <div className="overflow-x-auto">
              <h3 className="text-md font-bold text-gray-800 mb-2">Dettaglio Colonne</h3>
              <table className="min-w-full text-sm text-left text-gray-500">
                <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                  <tr>
                    <th className="px-4 py-2">Colonna</th>
                    <th className="px-4 py-2">Descrizione</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="bg-white border-b">
                    <td className="px-4 py-2 font-medium text-gray-900">Data/Ora</td>
                    <td className="px-4 py-2">Timestamp esatto dell'evento.</td>
                  </tr>
                  <tr className="bg-white border-b">
                    <td className="px-4 py-2 font-medium text-gray-900">Severità</td>
                    <td className="px-4 py-2">Livello di rischio (Low, Medium, Critical).</td>
                  </tr>
                  <tr className="bg-white border-b">
                    <td className="px-4 py-2 font-medium text-gray-900">Utente</td>
                    <td className="px-4 py-2">Username dell'operatore che ha eseguito l'azione.</td>
                  </tr>
                  <tr className="bg-white border-b">
                    <td className="px-4 py-2 font-medium text-gray-900">IP & Geo</td>
                    <td className="px-4 py-2">Indirizzo IP e posizione geografica stimata.</td>
                  </tr>
                  <tr className="bg-white border-b">
                    <td className="px-4 py-2 font-medium text-gray-900">Device ID</td>
                    <td className="px-4 py-2">Identificativo hardware univoco della macchina.</td>
                  </tr>
                  <tr className="bg-white border-b">
                    <td className="px-4 py-2 font-medium text-gray-900">Azione & Categoria</td>
                    <td className="px-4 py-2">Tipo di operazione (es. LOGIN, UPDATE) e modulo coinvolto.</td>
                  </tr>
                  <tr className="bg-white border-b">
                    <td className="px-4 py-2 font-medium text-gray-900">Dettagli & Modifiche</td>
                    <td className="px-4 py-2">Descrizione estesa. Passa il mouse su [Modifiche] per vedere il JSON dei campi cambiati (Vecchio {'->'} Nuovo).</td>
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

        {/* Database Sicuro */}
        <section>
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-600" />
            Architettura di Sicurezza Database
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="font-bold text-gray-800 mb-2 flex items-center gap-2">
                    <Shield className="w-4 h-4 text-green-500" /> Crittografia "At Rest"
                </h3>
                <p className="text-sm text-gray-600">
                    Il file database (<code>database_documenti.db</code>) è salvato su disco interamente crittografato (algoritmo AES-128 Fernet).
                    È illeggibile per qualsiasi strumento esterno. La decrittazione avviene esclusivamente nella memoria RAM volatile durante l'uso.
                </p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="font-bold text-gray-800 mb-2 flex items-center gap-2">
                    <Lock className="w-4 h-4 text-orange-500" /> Accesso Esclusivo (.lock)
                </h3>
                <p className="text-sm text-gray-600">
                    Al login, viene generato un file <code>.lock</code> che impedisce l'apertura simultanea da parte di altri utenti.
                    Il file viene rimosso automaticamente alla chiusura. Questo garantisce l'integrità dei dati in ambienti mono-utente.
                </p>
            </div>
             <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="font-bold text-gray-800 mb-2 flex items-center gap-2">
                    <Lock className="w-4 h-4 text-purple-500" /> Gestione Concorrenza (Multi-Utente)
                </h3>
                <p className="text-sm text-gray-600">
                    Il sistema di blocco a livello di sistema operativo (OS-level lock) garantisce che solo un utente alla volta possa avere i permessi di scrittura sul database.
                    Se un secondo utente apre l'applicazione mentre è già in uso, Intelleo si avvierà in modalità <strong>Sola Lettura</strong>, garantendo la consistenza dei dati.
                </p>
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
