import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LifeBuoy,
  AlertTriangle,
  WifiOff,
  FileWarning,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  Server
} from 'lucide-react';

const AccordionItem = ({ question, answer, icon: Icon, isOpen, onClick }) => {
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white mb-4 shadow-sm hover:shadow-md transition-shadow">
      <button
        onClick={onClick}
        className="w-full flex items-center justify-between p-4 text-left bg-white hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${isOpen ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'}`}>
            <Icon size={20} />
          </div>
          <span className="font-semibold text-gray-800">{question}</span>
        </div>
        {isOpen ? <ChevronUp size={20} className="text-gray-400" /> : <ChevronDown size={20} className="text-gray-400" />}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="p-4 pt-0 border-t border-gray-100 bg-gray-50/50 text-gray-600 leading-relaxed text-sm">
              <div className="pt-4">
                {answer}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const TroubleshootingGuide = () => {
  const [openIndex, setOpenIndex] = useState(0);

  const items = [
    {
      question: "Errore 429: Resource Exhausted (Quota AI Superata)",
      icon: Server,
      answer: (
        <>
          <p className="mb-2">
            Questo errore indica che hai raggiunto il limite di richieste del piano gratuito di Google Gemini (2.5 Pro).
          </p>
          <ul className="list-disc list-inside space-y-1 mb-2">
            <li><strong>Causa:</strong> Troppi documenti inviati in un breve lasso di tempo.</li>
            <li><strong>Soluzione:</strong> Attendi circa 1-2 minuti prima di riprovare.</li>
            <li><strong>Fix Permanente:</strong> Passa a un piano a pagamento (Pay-as-you-go) nella Google Cloud Console se devi elaborare grandi volumi di dati quotidianamente.</li>
          </ul>
        </>
      )
    },
    {
      question: "Errore Connessione SMTP (Invio Email Fallito)",
      icon: WifiOff,
      answer: (
        <>
          <p className="mb-2">
            Se l'invio delle email fallisce, verifica i seguenti punti in <em>Configurazione</em>:
          </p>
          <ol className="list-decimal list-inside space-y-1">
            <li><strong>Credenziali:</strong> Assicurati che l'indirizzo email e la password siano corretti. Per Gmail, DEVI usare una <strong>App Password</strong>, non la tua password di login abituale.</li>
            <li><strong>Porta e Sicurezza:</strong>
              <ul className="list-disc list-inside ml-4 mt-1 text-gray-500">
                <li>Porta <strong>465</strong> richiede SSL (implicito).</li>
                <li>Porta <strong>587</strong> richiede STARTTLS.</li>
              </ul>
            </li>
            <li><strong>Firewall:</strong> Verifica che il firewall aziendale o Windows Defender non stia bloccando le connessioni in uscita sulla porta 465/587.</li>
          </ol>
        </>
      )
    },
    {
      question: "Licenza Scaduta",
      icon: ShieldAlert,
      answer: (
        <>
          <p className="mb-2">
            L'applicazione richiede una licenza attiva per funzionare.
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li>Se vedi il messaggio <strong>"Licenza SCADUTA"</strong> nella schermata di login, contatta l'amministratore di sistema o il fornitore per il rinnovo.</li>
            <li>La cartella <code>Licenza</code> (contenente <code>config.dat</code>) deve essere presente nella directory di installazione. Non eliminare o modificare questi file.</li>
          </ul>
        </>
      )
    },
    {
      question: "Errori Importazione PDF (File non analizzato)",
      icon: FileWarning,
      answer: (
        <>
          <p className="mb-2">
            Se un file viene spostato nella cartella <code>NON ANALIZZATI</code> o genera errore:
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li><strong>Corruzione:</strong> Il file PDF potrebbe essere danneggiato. Prova ad aprirlo con Adobe Reader.</li>
            <li><strong>Password:</strong> I file protetti da password non possono essere letti dall'AI. Rimuovi la protezione e riprova.</li>
            <li><strong>Scansione Ileggibile:</strong> Se il PDF è una scansione di bassissima qualità (immagine sgranata), l'AI potrebbe non riuscire a leggere il testo.</li>
          </ul>
        </>
      )
    },
    {
      question: "File Non Valido (Firma non riconosciuta)",
      icon: AlertTriangle,
      answer: (
        <>
          <p>
            Per sicurezza, il sistema verifica la "firma digitale" interna dei file (Magic Numbers).
          </p>
          <p className="mt-2">
            Se ricevi questo errore, significa che un file con estensione <code>.pdf</code> o <code>.csv</code> non è realmente di quel formato (es. un file .exe rinominato). Il caricamento viene bloccato per prevenire rischi di sicurezza.
          </p>
        </>
      )
    },
    {
      question: "Errore critico all'avvio: 'Database bloccato'",
      icon: ShieldAlert,
      answer: (
        <>
          <p className="mb-2">
            Questo errore indica che il database è già in uso da un'altra istanza di Intelleo (o è rimasto bloccato dopo una chiusura anomala).
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li><strong>Causa:</strong> Il sistema di sicurezza impedisce l'accesso concorrente per proteggere i dati.</li>
            <li><strong>Soluzione:</strong> Verifica che non ci siano altre finestre di Intelleo aperte sulla stessa macchina. Se il problema persiste, riavvia il PC o elimina manualmente il file <code>.database_documenti.db.lock</code> nella cartella del database.</li>
          </ul>
        </>
      )
    }
  ];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-red-100 rounded-lg text-red-700">
            <LifeBuoy size={24} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Risoluzione Problemi</h1>
        </div>
        <p className="text-lg text-gray-500 ml-14">
          Soluzioni rapide ai problemi più comuni riscontrati durante l'utilizzo di Intelleo.
        </p>
      </motion.div>

      {/* Accordion List */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        {items.map((item, index) => (
          <AccordionItem
            key={index}
            question={item.question}
            answer={item.answer}
            icon={item.icon}
            isOpen={openIndex === index}
            onClick={() => setOpenIndex(index === openIndex ? -1 : index)}
          />
        ))}
      </motion.div>
    </div>
  );
};

export default TroubleshootingGuide;
