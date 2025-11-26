import React from 'react';
import { motion } from 'framer-motion';
import { FileText, UploadCloud, FolderOpen, Cpu, CheckCircle, AlertTriangle, List, ScanText } from 'lucide-react';

const Section = ({ title, children }) => (
  <section className="mb-12">
    <h2 className="text-2xl font-bold text-gray-800 mb-4 border-b border-gray-200 pb-2">{title}</h2>
    <div className="text-gray-600 leading-relaxed space-y-4">
      {children}
    </div>
  </section>
);

const ImportGuide = () => {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-purple-100 rounded-lg text-purple-700">
            <FileText size={24} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Importazione & AI</h1>
        </div>
        <p className="text-lg text-gray-500 ml-14">
          Automatizza l'inserimento dati grazie all'Intelligenza Artificiale. Trascina, analizza e organizza i tuoi documenti in pochi secondi.
        </p>
      </motion.div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

        <Section title="Come Funziona">
          <p>
            Intelleo utilizza un motore AI avanzato (<strong>Gemini 2.5 Pro</strong>) per leggere il contenuto dei tuoi PDF come farebbe un umano. Non si basa su template fissi, ma "capisce" il documento.
          </p>
          <ul className="space-y-3 mt-4">
            <li className="flex items-start gap-3">
              <UploadCloud size={20} className="text-blue-500 mt-1 shrink-0" />
              <span>
                <strong>Drag & Drop:</strong> Trascina intere cartelle o singoli file nell'area di importazione.
              </span>
            </li>
            <li className="flex items-start gap-3">
              <Cpu size={20} className="text-purple-500 mt-1 shrink-0" />
              <span>
                <strong>Analisi AI:</strong> Il sistema estrae automaticamente il <strong>DIPENDENTE</strong>, il <strong>CORSO/VISITA MEDICA</strong>, la <strong>DATA EMISSIONE</strong> e la scadenza.
              </span>
            </li>
            <li className="flex items-start gap-3">
              <FolderOpen size={20} className="text-orange-500 mt-1 shrink-0" />
              <span>
                <strong>Organizzazione Automatica:</strong> I file vengono rinominati e spostati in una struttura di cartelle creata automaticamente.
              </span>
            </li>
          </ul>
        </Section>

        <Section title="Struttura Gerarchica File">
            <p>
                Dopo l'analisi, i file vengono riorganizzati in una struttura di cartelle standardizzata all'interno della cartella di origine:
            </p>
            <div className="mt-4 bg-gray-50 p-6 rounded-lg border border-gray-200 font-mono text-sm">
                <div className="flex items-center gap-2">
                    <span>-</span>
                    <span className="font-semibold text-blue-700">📁 DOCUMENTI DIPENDENTI</span>
                </div>
                <div className="ml-6 border-l border-gray-300 pl-4">
                  <div className="flex items-center gap-2 mt-2">
                      <span>L</span>
                      <span className="text-purple-700">📁 NOME COGNOME (MATRICOLA)</span>
                  </div>
                   <div className="ml-6 border-l border-gray-300 pl-4">
                      <div className="flex items-center gap-2 mt-2">
                          <span>L</span>
                          <span className="text-green-700">📁 CATEGORIA</span>
                      </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-4">
                    <span>-</span>
                    <span className="font-semibold text-orange-700">📁 DOCUMENTI ANALIZZATI ASSENZA MATRICOLE</span>
                </div>
                <div className="flex items-center gap-2 mt-2">
                    <span>-</span>
                    <span className="font-semibold text-red-700">📁 DOCUMENTI NON ANALIZZATI</span>
                </div>
            </div>
        </Section>

        <Section title="Monitoraggio Avanzamento">
          <p>
            Durante l'analisi, una barra di avanzamento ti tiene aggiornato in tempo reale:
          </p>
          <div className="mt-4 bg-gray-100 p-4 rounded-lg border border-gray-200">
              <img src="/assets/progress_bar.png" alt="Progress Bar" className="rounded-md shadow-md" />
          </div>
          <ul className="space-y-3 mt-4 text-sm">
               <li className="flex items-center gap-2 text-gray-700">
                 <span className="font-bold text-blue-600">Conteggio:</span> "File X di Y"
               </li>
               <li className="flex items-center gap-2 text-gray-700">
                 <span className="font-bold text-blue-600">Tempo Rimanente:</span> Una stima (ETR) del tempo necessario per completare l'analisi.
               </li>
                <li className="flex items-center gap-2 text-gray-700">
                    <span className="font-bold text-red-600">Stop Sicuro:</span> Interrompe l'analisi dopo aver completato il file corrente, per non lasciare operazioni a metà.
                </li>
          </ul>
        </Section>

        <Section title="Categorie Supportate & Validità">
           <p className="mb-2 text-sm">
             Il sistema riconosce una vasta gamma di documenti. Alcuni hanno una scadenza fissa, altri sono considerati validi indefinitamente (salvo diversa indicazione nel documento).
           </p>
           <div className="bg-purple-50 p-4 rounded-lg border border-purple-100 max-h-64 overflow-y-auto custom-scrollbar">
             <ul className="space-y-2 text-sm text-purple-900">
               <li><span className="font-bold">ANTINCENDIO</span> (5 Anni)</li>
               <li><span className="font-bold">PRIMO SOCCORSO</span> (3 Anni)</li>
               <li><span className="font-bold">PLE</span> (5 Anni)</li>
               <li><span className="font-bold">GRU</span> (5 Anni)</li>
               <li><span className="font-bold">ATEX</span> (5 Anni)</li>
               <li><span className="font-bold">PREPOSTO</span> (2 Anni)</li>
               <li><span className="font-bold">BLSD</span> (1 Anno)</li>
               <li className="pt-2 border-t border-purple-200 mt-2"><span className="font-bold text-purple-700">Nessuna scadenza.</span></li>
               <li>• NOMINA</li>
               <li>• MEDICO COMPETENTE</li>
               <li>• HLO / TESSERA HLO</li>
               <li>• UNILAV</li>
               <li>• PATENTE</li>
               <li>• MODULO RECESSO RAPPORTO DI LAVORO</li>
             </ul>
           </div>
           <p className="text-xs text-gray-500 mt-2 italic">
             Nota: Per le categorie a validità indefinita, la scadenza viene impostata solo se esplicitamente trovata nel testo (es. data fine rapporto, validità patente).
           </p>
        </Section>
      </div>

      <Section title="Consigli per una Scansione Ottimale">
        <div className="flex items-start gap-4 bg-gray-50 p-6 rounded-lg border border-gray-200">
           <div className="p-3 bg-white rounded-full shadow-sm text-purple-600">
             <ScanText size={24} />
           </div>
           <div>
             <h3 className="font-bold text-gray-900 mb-2">Aiuta l'AI a leggere meglio</h3>
             <p className="text-gray-600 mb-4 text-sm">
               L'Intelligenza Artificiale è potente, ma la qualità del documento originale è fondamentale per evitare errori di lettura.
             </p>
             <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <ul className="space-y-2">
                   <li className="flex items-center gap-2 text-gray-700">
                     <span className="w-2 h-2 rounded-full bg-green-500"></span>
                     <span>Usa PDF originali (generati da PC) quando possibile.</span>
                   </li>
                   <li className="flex items-center gap-2 text-gray-700">
                     <span className="w-2 h-2 rounded-full bg-green-500"></span>
                     <span>Per le scansioni, imposta almeno <strong>300 DPI</strong>.</span>
                   </li>
                </ul>
                <ul className="space-y-2">
                   <li className="flex items-center gap-2 text-gray-700">
                     <span className="w-2 h-2 rounded-full bg-red-500"></span>
                     <span>Evita timbri sopra le date o i nomi.</span>
                   </li>
                   <li className="flex items-center gap-2 text-gray-700">
                     <span className="w-2 h-2 rounded-full bg-red-500"></span>
                     <span>Evita scansioni storte o sfuocate (foto da cellulare).</span>
                   </li>
                </ul>
             </div>
           </div>
        </div>
      </Section>

      <Section title="Gestione dei File Analizzati">
        <p className="mb-4">
          I file vengono gestiti e rinominati in modo diverso a seconda dell'esito dell'analisi AI:
        </p>

        <div className="mt-4 space-y-4">
            <div className="p-4 rounded-lg border bg-green-50 border-green-200">
              <h4 className="font-bold text-green-800 mb-2">Caso 1: Successo Completo</h4>
              <p className="text-sm text-green-700 mb-3">
                Se il file viene analizzato e associato correttamente a un dipendente, viene rinominato e spostato in <code>DOCUMENTI DIPENDENTI</code>.
              </p>
              <div className="bg-white text-gray-700 p-3 rounded-md font-mono text-xs shadow-sm border">
                COGNOME NOME (MATRICOLA) - CATEGORIA - SCADENZA.pdf
              </div>
            </div>

            <div className="p-4 rounded-lg border bg-orange-50 border-orange-200">
              <h4 className="font-bold text-orange-800 mb-2">Caso 2: Analizzato ma Non Associato (Orfano)</h4>
              <p className="text-sm text-orange-700">
                Se l'AI estrae i dati ma non trova un dipendente corrispondente (es. matricola assente), il file originale viene spostato in <code>DOCUMENTI ANALIZZATI ASSENZA MATRICOLE</code>. Potrai assegnarlo manualmente dalla sezione <strong>Convalida Dati</strong>.
              </p>
            </div>

            <div className="p-4 rounded-lg border bg-red-50 border-red-200">
              <h4 className="font-bold text-red-800 mb-2">Caso 3: Errore di Analisi</h4>
              <p className="text-sm text-red-700">
                Se si verifica un errore (es. PDF corrotto, illeggibile), il file originale viene spostato in <code>DOCUMENTI NON ANALIZZATI</code> per una verifica manuale.
              </p>
            </div>
        </div>
      </Section>
    </div>
  );
};

export default ImportGuide;
