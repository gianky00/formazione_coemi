import React from 'react';
import GuideCard from '../components/ui/GuideCard';
import Note from '../components/ui/Note';
import Step from '../components/ui/Step';
import ValidationSimulator from '../components/ValidationSimulator';
import { Database, CheckCircle, AlertOctagon } from 'lucide-react';

const ValidationGuide = () => {
  return (
    <div className="space-y-12">
      {/* Header */}
      <div className="max-w-3xl">
        <h1 className="h1">Convalida Dati</h1>
        <p className="text-body text-xl">
          Il tuo centro di controllo qualità. Qui revisioni i documenti che l'AI ha analizzato ma che richiedono una conferma umana prima di entrare nel database.
        </p>
      </div>

      {/* Simulator */}
      <section>
         <h2 className="h2 flex items-center gap-2">
            <CheckCircle className="text-green-600" />
            Prova la Convalida
        </h2>
        <p className="text-body mb-6">
            In questa simulazione, puoi approvare (✓) o rifiutare (✕) i documenti. Nota come spariscono dalla lista una volta processati.
        </p>
        <ValidationSimulator />
      </section>

      {/* Workflow Steps */}
      <section className="mt-12">
        <h2 className="h2">Il Flusso di Lavoro</h2>
        <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm">
            <Step number="1" title="Revisione">
                <p>Controlla i dati estratti (Nome, Categoria, Data). Se vedi un'etichetta <span className="text-red-500 font-bold">Dati Incerti</span> o <span className="text-orange-500 font-bold">???</span>, fai particolare attenzione.</p>
            </Step>
            <Step number="2" title="Anteprima">
                <p>Clicca sull'icona dell'occhio per aprire il PDF originale a schermo intero e verificare la correttezza delle informazioni lette dall'AI.</p>
            </Step>
            <Step number="3" title="Azione">
                <ul className="list-disc pl-5 space-y-2 mt-2">
                    <li><strong>Approva (Verde):</strong> Il certificato viene salvato nel database ufficiale e il file spostato nella cartella del dipendente.</li>
                    <li><strong>Rifiuta (Rosso):</strong> Il file viene cancellato o marcato come errore, e non entra nel database.</li>
                    <li><strong>Modifica (Matita):</strong> Se i dati sono quasi corretti (es. data sbagliata di un giorno), correggili prima di approvare.</li>
                </ul>
            </Step>
        </div>
      </section>

      {/* Tips */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Note type="tip" title="Scorciatoia">
              Puoi selezionare più righe contemporaneamente (tieni premuto CTRL) e approvarle in blocco se sei sicuro che siano corrette.
          </Note>
          <Note type="warning" title="Attenzione ai 'Falsi Positivi'">
              A volte l'AI può scambiare una data di nascita per una data di scadenza. Controlla sempre le date nei documenti più vecchi o mal scansionati.
          </Note>
      </section>

    </div>
  );
};

export default ValidationGuide;
