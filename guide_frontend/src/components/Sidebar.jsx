import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Database,
  FileText,
  Calendar,
  Settings,
  Users,
  ChevronRight,
  ChevronLeft,
  BookOpen,
  X,
  Shield,
  LifeBuoy,
  HardDrive,
  Book,
  Keyboard
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

const SidebarItem = ({ icon: Icon, label, to, collapsed }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      className={clsx(
        "flex items-center gap-3 p-3 rounded-lg transition-colors mb-1 group relative",
        isActive
          ? "bg-intelleo-accent text-white shadow-md"
          : "text-blue-100 hover:bg-blue-800/50 hover:text-white"
      )}
    >
      <Icon size={20} className="shrink-0" />
      {!collapsed && (
        <motion.span
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="font-medium whitespace-nowrap"
        >
          {label}
        </motion.span>
      )}

      {/* Tooltip for collapsed state */}
      {collapsed && (
        <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none z-50 whitespace-nowrap">
          {label}
        </div>
      )}
    </Link>
  );
};

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [bridge, setBridge] = useState(null);

  useEffect(() => {
    if (window.qt && window.qt.webChannelTransport) {
      new window.QWebChannel(window.qt.webChannelTransport, function(channel) {
        if (channel.objects.bridge) {
            setBridge(channel.objects.bridge);
        }
      });
    }
  }, []);

  const handleClose = () => {
    if (bridge) {
        bridge.closeWindow();
    } else {
      console.warn("Qt WebChannel bridge not available");
    }
  };

  return (
    <motion.div
      className="h-screen bg-intelleo-primary flex flex-col shadow-xl z-50 relative"
      animate={{ width: collapsed ? 64 : 260 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-blue-800">
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="font-bold text-white text-xl tracking-tight"
          >
            Intelleo<span className="text-blue-300">Guide</span>
          </motion.div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-md bg-blue-800 text-blue-100 hover:text-white hover:bg-blue-700 transition-colors"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Nav Items */}
      <div className="flex-1 py-6 px-2 overflow-y-auto custom-scrollbar">
        <SidebarItem icon={BookOpen} label="Panoramica" to="/" collapsed={collapsed} />

        <div className="my-2 border-t border-blue-800/50 mx-2"></div>

        <SidebarItem icon={LayoutDashboard} label="Database" to="/database" collapsed={collapsed} />
        <SidebarItem icon={FileText} label="Importazione & AI" to="/import" collapsed={collapsed} />
        <SidebarItem icon={Database} label="Convalida Dati" to="/validation" collapsed={collapsed} />
        <SidebarItem icon={Calendar} label="Scadenzario" to="/calendar" collapsed={collapsed} />
        <SidebarItem icon={Users} label="Dipendenti" to="/employees" collapsed={collapsed} />

        <div className="my-2 border-t border-blue-800/50 mx-2"></div>

        <SidebarItem icon={Shield} label="Sicurezza & Audit" to="/security" collapsed={collapsed} />
        <SidebarItem icon={Settings} label="Configurazione" to="/settings" collapsed={collapsed} />
        <SidebarItem icon={HardDrive} label="Backup & Manutenzione" to="/maintenance" collapsed={collapsed} />

        <div className="my-2 border-t border-blue-800/50 mx-2"></div>

        <SidebarItem icon={Book} label="Glossario" to="/glossary" collapsed={collapsed} />
        <SidebarItem icon={Keyboard} label="Scorciatoie" to="/shortcuts" collapsed={collapsed} />
        <SidebarItem icon={LifeBuoy} label="Risoluzione Problemi" to="/troubleshooting" collapsed={collapsed} />

        <div className="mt-4 border-t border-blue-800/50 mx-2 pt-2">
            <button
                onClick={handleClose}
                className={clsx(
                    "w-full flex items-center gap-3 p-3 rounded-lg transition-colors mb-1 group relative",
                    "text-blue-100 hover:bg-red-900/50 hover:text-white"
                )}
            >
                <X size={20} className="shrink-0" />
                {!collapsed && (
                    <motion.span
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="font-medium whitespace-nowrap"
                    >
                        Chiudi
                    </motion.span>
                )}
                {collapsed && (
                    <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none z-50 whitespace-nowrap">
                        Chiudi
                    </div>
                )}
            </button>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-blue-800 text-center">
        {!collapsed && (
          <p className="text-xs text-blue-300/60">v1.0.0 • Guida Interattiva</p>
        )}
      </div>
    </motion.div>
  );
};

export default Sidebar;
