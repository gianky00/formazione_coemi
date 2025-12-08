import React from 'react';
import GuideCard from '../components/ui/GuideCard';
import { Book } from 'lucide-react';

const Glossary = () => {
  const terms = [
    {
      term: "Matricola",
      def: "Il codice identificativo univoco (Badge) di un dipendente. Intelleo lo usa per collegare con certezza un certificato alla persona giusta."
    },
    {
      term: "Orfano",
      def: "Un certificato che è stato analizzato dall'AI ma per cui non è stato trovato un dipendente corrispondente nel database (es. perché la matricola era illeggibile o il dipendente non è ancora stato creato)."
    },
    {
      term: "Upsert",
      def: "Tecnica di importazione dati: se il dipendente esiste già, lo aggiorna; se non esiste, lo crea. Non cancella mai nulla."
    },
    {
      term: "Lock File",
      def: "Un file speciale (.lock) che il programma crea quando apri il database. Serve a dire agli altri PC \"Attenzione, sto scrivendo io qui!\", impedendo conflitti."
    },
    {
      term: "Hardware ID (HWID)",
      def: "Un codice alfanumerico univoco generato basandosi sui componenti fisici del tuo PC. Serve a legare la licenza software a quella specifica macchina."
    },
    {
      term: "SMTP",
      def: "Simple Mail Transfer Protocol. È il \"postino\" digitale. Le impostazioni SMTP dicono a Intelleo quale server usare per spedire le email di notifica."
    },
    {
      term: "Confidence Score",
      def: "Il grado di sicurezza (da 0 a 100%) che l'Intelligenza Artificiale assegna a una lettura. Se è basso, il sistema potrebbe segnare il dato come \"Incerto\"."
    },
    {
      term: "Gantt",
      def: "Un tipo di grafico a barre orizzontali usato nello Scadenzario per visualizzare la durata temporale dei certificati."
    }
  ];

  return (
    <div className="space-y-12">
      <div className="max-w-3xl">
        <h1 className="h1">Glossario</h1>
        <p className="text-body text-xl">
          Le definizioni dei termini tecnici usati in Intelleo.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {terms.map((item) => (
            <GuideCard key={item.term} className="hover:border-blue-300 transition-colors group">
                <h3 className="text-lg font-bold text-gray-900 mb-2 flex items-center gap-2 group-hover:text-blue-700">
                    <Book size={18} className="text-gray-400 group-hover:text-blue-500"/>
                    {item.term}
                </h3>
                <p className="text-gray-600 leading-relaxed text-sm">
                    {item.def}
                </p>
            </GuideCard>
        ))}
      </div>
    </div>
  );
};

export default Glossary;
