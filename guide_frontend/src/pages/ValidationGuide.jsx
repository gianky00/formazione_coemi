import React from 'react';
import { motion } from 'framer-motion';
import { Database, CheckSquare, UserX, Edit3, Trash2 } from 'lucide-react';

const Section = ({ title, children }) => (
  <section className="mb-12">
    <h2 className="text-2xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">{title}</h2>
    <div className="text-gray-600 leading-relaxed space-y-4">
      {children}
    </div>
  </section>
);

const ValidationGuide = () => {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-orange-100 rounded-lg text-orange-700">
            <Database size={24} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Convalida Dati</h1>
        </div>
        <p className="text-lg text-gray-500 ml-14">
          L'area di transito dove i dati estratti dall'AI vengono revisionati prima di diventare ufficiali.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Section title="Il Flusso di Lavoro">
          <p>
            I certificati appena analizzati non entrano direttamente nel Database principale. Appaiono prima nella vista <strong>Convalida Dati</strong>.
          </p>
          <ul className="space-y-3 mt-4">
            <li className="flex items-start gap-3">
              <div className="bg-gray-100 p-1 rounded text-gray-600 font-bold text-xs mt-1">1</div>
              <span>Controlla che i dati estratti (Date, Categoria) siano corretti.</span>
            </li>
            <li className="flex items-start gap-3">
              <div className="bg-gray-100 p-1 rounded text-gray-600 font-bold text-xs mt-1">2</div>
              <span>Verifica che il dipendente sia stato associato correttamente.</span>
            </li>
            <li className="flex items-start gap-3">
              <div className="bg-gray-100 p-1 rounded text-gray-600 font-bold text-xs mt-1">3</div>
              <span>Seleziona le righe corrette e clicca su <strong>"Convalida"</strong>.</span>
            </li>
          </ul>
        </Section>

        <Section title="Certificati Orfani">
          <div className="flex items-start gap-3 bg-red-50 p-4 rounded-lg border border-red-100">
            <UserX size={24} className="text-red-500 mt-1 shrink-0" />
            <div>
              <h3 className="font-bold text-red-800 mb-1">Dipendente Non Trovato</h3>
              <p className="text-sm text-red-700 mb-2">
                Se l'AI non riesce ad associare un certificato ad un dipendente esistente (es. matricola mancante o nome errato), il campo Dipendente apparirà vuoto o evidenziato.
              </p>
              <p className="text-sm text-red-700 font-medium">
                Usa il tasto "Modifica" per assegnare manualmente il certificato al dipendente corretto.
              </p>
            </div>
          </div>
        </Section>
      </div>

      <Section title="Strumenti di Revisione">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-gray-200 rounded hover:shadow-md transition-shadow">
            <div className="flex items-center gap-2 text-blue-600 font-bold mb-2">
              <Edit3 size={18} /> Modifica
            </div>
            <p className="text-sm text-gray-500">
              Doppio click su una riga o usa il tasto Modifica per correggere date o categorie errate.
            </p>
          </div>
          <div className="p-4 border border-gray-200 rounded hover:shadow-md transition-shadow">
            <div className="flex items-center gap-2 text-green-600 font-bold mb-2">
              <CheckSquare size={18} /> Convalida Multipla
            </div>
            <p className="text-sm text-gray-500">
              Tieni premuto <code>CTRL</code> o <code>SHIFT</code> per selezionare più righe e convalidarle in blocco.
            </p>
          </div>
          <div className="p-4 border border-gray-200 rounded hover:shadow-md transition-shadow">
            <div className="flex items-center gap-2 text-red-600 font-bold mb-2">
              <Trash2 size={18} /> Elimina
            </div>
            <p className="text-sm text-gray-500">
              Rimuove il record dal database. Il file PDF originale <strong>non</strong> viene cancellato dal disco.
            </p>
          </div>
        </div>
      </Section>
    </div>
  );
};

export default ValidationGuide;
