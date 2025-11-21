import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import DashboardGuide from './pages/DashboardGuide';
import { Construction } from 'lucide-react';

const UnderConstruction = ({ title }) => (
  <div className="flex flex-col items-center justify-center h-full text-gray-400">
    <Construction size={64} className="mb-4 opacity-50" />
    <h2 className="text-2xl font-bold mb-2">{title}</h2>
    <p>Questa guida è in fase di sviluppo.</p>
  </div>
);

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="dashboard" element={<DashboardGuide />} />
        <Route path="import" element={<UnderConstruction title="Importazione & AI" />} />
        <Route path="validation" element={<UnderConstruction title="Convalida Dati" />} />
        <Route path="calendar" element={<UnderConstruction title="Scadenzario" />} />
        <Route path="employees" element={<UnderConstruction title="Dipendenti" />} />
        <Route path="settings" element={<UnderConstruction title="Configurazione" />} />
      </Route>
    </Routes>
  );
}

export default App;
