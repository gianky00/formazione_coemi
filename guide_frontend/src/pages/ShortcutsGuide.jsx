import React from 'react';
import GuideCard from '../components/ui/GuideCard';
import { Keyboard, Command } from 'lucide-react';
import PropTypes from 'prop-types';

const ShortcutRow = ({ keys, desc }) => (
  <div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0 hover:bg-gray-50 px-2 rounded-lg transition-colors">
      <span className="text-gray-700 font-medium text-sm">{desc}</span>
      <div className="flex gap-1">
          {keys.map((k, i) => (
              <span key={`key-${i}`} className="kbd">{k}</span>
          ))}
      </div>
  </div>
);

ShortcutRow.propTypes = {
  keys: PropTypes.arrayOf(PropTypes.string).isRequired,
  desc: PropTypes.string.isRequired,
};

const ShortcutsGuide = () => {
  return (
    <div className="space-y-12">
      <div className="max-w-3xl">
        <h1 className="h1">Scorciatoie da Tastiera</h1>
        <p className="text-body text-xl">
          Diventa un power user. Risparmia tempo usando la tastiera invece del mouse.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

          <section>
              <h2 className="h2 flex items-center gap-2"><Command className="text-blue-600"/> Navigazione & App</h2>
              <GuideCard>
                  <ShortcutRow keys={['F1']} desc="Apri questa Guida" />
                  <ShortcutRow keys={['Alt', 'F4']} desc="Chiudi Applicazione" />
                  <ShortcutRow keys={['Ctrl', '+']} desc="Zoom Avanti (Interfaccia)" />
                  <ShortcutRow keys={['Ctrl', '-']} desc="Zoom Indietro" />
              </GuideCard>
          </section>

          <section>
              <h2 className="h2 flex items-center gap-2"><Keyboard className="text-purple-600"/> Tabelle & Dati</h2>
              <GuideCard>
                  <ShortcutRow keys={['Ctrl', 'Click']} desc="Selezione Multipla Righe" />
                  <ShortcutRow keys={['Shift', 'Click']} desc="Selezione Intervallo Righe" />
                  <ShortcutRow keys={['Doppio Click']} desc="Modifica/Dettaglio Riga" />
                  <ShortcutRow keys={['Canc']} desc="Elimina Riga Selezionata" />
                  <ShortcutRow keys={['Ctrl', 'C']} desc="Copia cella selezionata" />
              </GuideCard>
          </section>

          <section>
              <h2 className="h2 flex items-center gap-2">Scadenzario Grafico</h2>
              <GuideCard>
                  <ShortcutRow keys={['Rotella Mouse']} desc="Scorri Verticalmente" />
                  <ShortcutRow keys={['Shift', 'Rotella']} desc="Scorri Temporalmente (Orizzontale)" />
                  <ShortcutRow keys={['Ctrl', 'Rotella']} desc="Zoom Timeline (In/Out)" />
              </GuideCard>
          </section>

      </div>
    </div>
  );
};

export default ShortcutsGuide;
