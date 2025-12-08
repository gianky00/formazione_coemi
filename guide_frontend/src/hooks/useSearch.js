import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const SEARCH_INDEX = [
  { title: "Panoramica", path: "/", keywords: "home inizio start introduzione" },
  { title: "Database", path: "/database", keywords: "tabella dati ricerca filtro modifica cancella certificati" },
  { title: "Importazione AI", path: "/import", keywords: "upload pdf trascina drag drop analisi intelligenza artificiale" },
  { title: "Convalida Dati", path: "/validation", keywords: "verifica approva orfani errori matricola" },
  { title: "Scadenzario", path: "/calendar", keywords: "gantt scadenze tempo rinnovo timeline" },
  { title: "Dipendenti", path: "/employees", keywords: "personale anagrafica csv importazione" },
  { title: "Sicurezza", path: "/security", keywords: "password crittografia audit log gdpr" },
  { title: "Configurazione", path: "/settings", keywords: "email smtp opzioni preferenze" },
  { title: "Backup & Manutenzione", path: "/maintenance", keywords: "ripristino salvataggio migrazione" },
  { title: "Risoluzione Problemi", path: "/troubleshooting", keywords: "errori bug crash aiuto supporto" },
  { title: "Glossario", path: "/glossary", keywords: "termini definizioni vocabolario" },
  { title: "Scorciatoie", path: "/shortcuts", keywords: "tastiera comandi rapidi hotkeys" },
];

export const useSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    const lowerQuery = query.toLowerCase();
    const filtered = SEARCH_INDEX.filter(item =>
      item.title.toLowerCase().includes(lowerQuery) ||
      item.keywords.includes(lowerQuery)
    );
    setResults(filtered);
  }, [query]);

  const selectResult = (path) => {
    navigate(path);
    setQuery('');
    setResults([]);
  };

  return { query, setQuery, results, selectResult };
};
