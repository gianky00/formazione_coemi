import React from 'react';
import GuideCard from '../components/ui/GuideCard';
import Note from '../components/ui/Note';
import Accordion from '../components/ui/Accordion';
import { HelpCircle, WifiOff, FileX, ShieldAlert } from 'lucide-react';

const TroubleshootingGuide = () => {
  const faqItems = [
    {
      title: "Errore: \"Database Locked\" o \"Sola Lettura\"",
      content: (
        <div>
          <p className="mb-2">Questo accade se un altro utente (o un'altra istanza di Intelleo) ha già aperto il database.</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Chiudi Intelleo su tutti gli altri PC.</li>
            <li>Controlla se hai aperto l'app due volte sullo stesso PC.</li>
            <li>Se il problema persiste, riavvia il computer per sbloccare i file.</li>
          </ul>
        </div>
      )
    },
    {
      title: "L'importazione AI è lenta o ferma",
      content: (
        <div>
          <p className="mb-2">L'analisi dipende dalla connessione internet e dai server Google Gemini.</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Verifica la tua connessione internet.</li>
            <li>Se stai caricando PDF molto pesanti (&gt;20MB) o scansioni ad altissima risoluzione, l'upload potrebbe richiedere tempo.</li>
            <li>Prova a riavviare l'importazione con meno file per volta (es. 10 alla volta).</li>
          </ul>
        </div>
      )
    },
    {
      title: "Email di test non arriva",
      content: (
        <div>
          <p className="mb-2">Spesso è un problema di configurazione SMTP.</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Se usi Gmail, <strong>DEVI</strong> usare una "App Password", non la tua password normale.</li>
            <li>Controlla la cartella Spam.</li>
            <li>Verifica che la porta sia 465 (SSL) o 587 (STARTTLS).</li>
            <li>Controlla che l'antivirus aziendale non blocchi le connessioni in uscita sulla porta 465/587.</li>
          </ul>
        </div>
      )
    },
    {
      title: "Licenza scaduta o non valida",
      content: (
        <div>
          <p className="mb-2">Se vedi un avviso di licenza:</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Assicurati di essere connesso a internet (necessario per il controllo periodico).</li>
            <li>Verifica la data di scadenza in <strong>Configurazione</strong>.</li>
            <li>Contatta il supporto fornendo il tuo <strong>Hardware ID</strong> visualizzato nella schermata di errore.</li>
          </ul>
        </div>
      )
    },
    {
      title: "Il PDF non si apre dall'applicazione",
      content: (
        <div>
          <p className="mb-2">Intelleo usa il visualizzatore PDF predefinito del tuo sistema.</p>
          <ul className="list-disc pl-5 space-y-1">
            <li>Verifica di avere Adobe Reader o un browser (Edge/Chrome) impostato come default per i .pdf.</li>
            <li>Controlla se il file esiste ancora sul disco (potrebbe essere stato spostato o cancellato manualmente).</li>
          </ul>
        </div>
      )
    }
  ];

  return (
    <div className="space-y-12">
      <div className="max-w-3xl">
        <h1 className="h1">Risoluzione Problemi</h1>
        <p className="text-body text-xl">
          Soluzioni rapide per gli errori più comuni. Prima di chiamare l'assistenza, prova questi passaggi.
        </p>
      </div>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <GuideCard title="Connessione" icon={WifiOff}>
             Problemi con l'AI o l'invio Email? Spesso dipende dalla rete o dal firewall.
         </GuideCard>
         <GuideCard title="File & Dati" icon={FileX}>
             Errori di lettura PDF o file spariti? Verifica i percorsi e i nomi dei file.
         </GuideCard>
         <GuideCard title="Accesso" icon={ShieldAlert}>
             Password dimenticata o Database bloccato? Gestione sessioni e lock file.
         </GuideCard>
      </section>

      <section>
          <h2 className="h2 flex items-center gap-2"><HelpCircle className="text-blue-600"/> FAQ Tecniche</h2>
          <Accordion items={faqItems} />
      </section>

      <section className="bg-blue-50 border border-blue-100 rounded-xl p-8 text-center mt-12">
          <h3 className="text-xl font-bold text-blue-900 mb-2">Hai ancora problemi?</h3>
          <p className="text-blue-700 mb-6">
              Se la guida non basta, il nostro team di supporto è a disposizione.
          </p>
          <div className="flex justify-center gap-4">
              <button className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm">
                  Apri Ticket Supporto
              </button>
              <button className="bg-white text-blue-700 border border-blue-200 px-6 py-2 rounded-lg font-medium hover:bg-blue-50 transition-colors">
                  Scarica Log Errori
              </button>
          </div>
          <p className="text-xs text-blue-400 mt-4">
              Includi sempre il file di Log quando contatti l'assistenza.
          </p>
      </section>
    </div>
  );
};

export default TroubleshootingGuide;
