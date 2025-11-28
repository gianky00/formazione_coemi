import React from 'react';
import GuideCard from '../components/ui/GuideCard';
import Note from '../components/ui/Note';
import Step from '../components/ui/Step';
import DashboardSimulator from '../components/DashboardSimulator';
import { Database, Filter, Search, Edit, Trash, Download } from 'lucide-react';

const DatabaseGuide = () => {
  return (
    <div className="space-y-12">
      {/* Header */}
      <div className="max-w-3xl">
        <h1 className="h1">Database & Dashboard</h1>
        <p className="text-body text-xl">
          Il cuore di Intelleo. Qui hai il controllo completo su tutti i certificati, le scadenze e lo stato di conformità della tua azienda.
        </p>
      </div>

      {/* Simulator Section */}
      <section>
        <h2 className="h2 flex items-center gap-2">
            <Database className="text-blue-600" />
            Prova Interattiva
        </h2>
        <p className="text-body mb-6">
          Questa è una simulazione fedele della tabella che troverai nell'applicazione. Prova a cercare "Rossi", filtrare i risultati o selezionare una riga per attivare i comandi.
        </p>
        <DashboardSimulator />
        <div className="mt-4 flex gap-4 overflow-x-auto pb-2">
           <Note type="tip" title="Suggerimento">
              Fai doppio clic su una riga (nella tabella reale) per aprire rapidamente i dettagli del certificato.
           </Note>
        </div>
      </section>

      {/* Features Detail */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <GuideCard title="Filtri Avanzati" icon={Filter}>
            <p className="mb-4">
                Usa i menu a tendina sopra la tabella per filtrare rapidamente per:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-sm">
                <li><strong>Dipendente:</strong> Mostra solo i documenti di una persona specifica.</li>
                <li><strong>Categoria:</strong> Vedi solo "Antincendio" o "Visite Mediche".</li>
                <li><strong>Stato:</strong> Isola solo i certificati "Scaduti" o "In Scadenza".</li>
            </ul>
        </GuideCard>

        <GuideCard title="Ricerca Rapida" icon={Search}>
            <p className="mb-4">
                La barra di ricerca è universale. Puoi digitare qualsiasi cosa:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-sm">
                <li>Nome del dipendente</li>
                <li>Tipo di corso (es. "PLE")</li>
                <li>Data di rilascio (es. "2023")</li>
            </ul>
            <p className="mt-4 text-sm text-gray-500 italic">I risultati vengono aggiornati in tempo reale mentre digiti.</p>
        </GuideCard>
      </section>

      {/* CRUD Operations */}
      <section>
        <h2 className="h2">Gestione dei Dati</h2>
        <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm">
            <Step number="1" title="Modifica un Certificato">
                <p>Seleziona una riga e clicca sul pulsante <strong>Modifica</strong> (icona matita <Edit size={14} className="inline"/>). Si aprirà una finestra dove potrai correggere le date o cambiare l'associazione col dipendente.</p>
            </Step>
            <Step number="2" title="Eliminazione">
                <p>Seleziona una o più righe (tenendo premuto CTRL) e clicca su <strong>Cancella</strong> (icona cestino <Trash size={14} className="inline"/>). Ti verrà chiesta una conferma prima della rimozione definitiva.</p>
            </Step>
            <Step number="3" title="Esportazione Excel/CSV">
                <p>Vuoi lavorare i dati altrove? Clicca sul pulsante <strong>Esporta</strong> <Download size={14} className="inline"/> in alto a destra per scaricare l'attuale vista (filtrata) in formato CSV compatibile con Excel.</p>
            </Step>
        </div>
      </section>

       <Note type="warning" title="Attenzione">
          L'eliminazione di un certificato dal Database è <strong>irreversibile</strong> e rimuove anche il file PDF associato dalla cartella del dipendente.
       </Note>

    </div>
  );
};

export default DatabaseGuide;
