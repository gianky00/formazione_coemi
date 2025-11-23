import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import DashboardGuide from './pages/DashboardGuide';
import ImportGuide from './pages/ImportGuide';
import ValidationGuide from './pages/ValidationGuide';
import CalendarGuide from './pages/CalendarGuide';
import EmployeesGuide from './pages/EmployeesGuide';
import SettingsGuide from './pages/SettingsGuide';
import SecurityGuide from './pages/SecurityGuide';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="dashboard" element={<DashboardGuide />} />
        <Route path="import" element={<ImportGuide />} />
        <Route path="validation" element={<ValidationGuide />} />
        <Route path="calendar" element={<CalendarGuide />} />
        <Route path="employees" element={<EmployeesGuide />} />
        <Route path="security" element={<SecurityGuide />} />
        <Route path="settings" element={<SettingsGuide />} />
      </Route>
    </Routes>
  );
}

export default App;
