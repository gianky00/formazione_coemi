import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import DatabaseGuide from './pages/DatabaseGuide';
import ImportGuide from './pages/ImportGuide';
import ValidationGuide from './pages/ValidationGuide';
import CalendarGuide from './pages/CalendarGuide';
import EmployeesGuide from './pages/EmployeesGuide';
import SettingsGuide from './pages/SettingsGuide';
import SecurityGuide from './pages/SecurityGuide';
import TroubleshootingGuide from './pages/TroubleshootingGuide';
import MaintenanceGuide from './pages/MaintenanceGuide';
import Glossary from './pages/Glossary';
import ShortcutsGuide from './pages/ShortcutsGuide';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="database" element={<DatabaseGuide />} />
        <Route path="import" element={<ImportGuide />} />
        <Route path="validation" element={<ValidationGuide />} />
        <Route path="calendar" element={<CalendarGuide />} />
        <Route path="employees" element={<EmployeesGuide />} />
        <Route path="security" element={<SecurityGuide />} />
        <Route path="settings" element={<SettingsGuide />} />
        <Route path="troubleshooting" element={<TroubleshootingGuide />} />
        <Route path="maintenance" element={<MaintenanceGuide />} />
        <Route path="glossary" element={<Glossary />} />
        <Route path="shortcuts" element={<ShortcutsGuide />} />
      </Route>
    </Routes>
  );
}

export default App;
