import React from 'react';
import { motion } from 'framer-motion';
import { LayoutDashboard, FileText, Database, Calendar, ArrowRight, LifeBuoy, Shield, HardDrive, Book, Keyboard, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';
import GuideCard from '../components/ui/GuideCard';

const Home = () => {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12 relative overflow-hidden">
        {/* Decorative background element */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-100 rounded-full blur-3xl opacity-30 -z-10 pointer-events-none"></div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <span className="inline-flex items-center gap-1.5 py-1 px-3 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold tracking-wide mb-6 border border-blue-100">
            <Zap size={12} className="fill-current" />
            GUIDA UFFICIALE 2025
          </span>
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 tracking-tight">
            Benvenuto in <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-700 to-blue-500">Intelleo</span>
          </h1>
          <p className="text-xl text-gray-500 max-w-2xl mx-auto leading-relaxed font-light">
            La piattaforma intelligente per la gestione automatizzata delle scadenze, formazione e sicurezza aziendale.
          </p>

          <div className="mt-8 flex justify-center gap-4">
             <Link to="/import" className="btn-primary flex items-center gap-2 px-6 py-3 shadow-lg shadow-blue-900/20">
                Inizia il Tutorial <ArrowRight size={18} />
             </Link>
             <Link to="/shortcuts" className="px-6 py-3 bg-white text-gray-700 font-medium rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors shadow-sm">
                Vedi Scorciatoie
             </Link>
          </div>
        </motion.div>
      </section>

      {/* Feature Grid */}
      <section>
        <div className="flex items-center justify-between mb-8 px-2">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Moduli Principali</h2>
            <p className="text-sm text-gray-500 mt-1">Seleziona un modulo per apprendere le funzionalità base.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link to="/dashboard" className="block h-full">
            <GuideCard className="h-full hover:border-blue-300 hover:shadow-lg group" delay={0.1}>
                <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-intelleo-accent mb-4 group-hover:scale-110 transition-transform duration-300">
                    <LayoutDashboard size={24} />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-intelleo-accent transition-colors">Dashboard & Database</h3>
                <p className="text-sm text-gray-500 mb-4">Monitora lo stato globale delle conformità, filtra certificati e gestisci scadenze in tempo reale.</p>
                <span className="text-sm font-semibold text-intelleo-accent flex items-center gap-1 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all">
                    Esplora <ArrowRight size={14} />
                </span>
            </GuideCard>
          </Link>

          <Link to="/import" className="block h-full">
            <GuideCard className="h-full hover:border-purple-300 hover:shadow-lg group" delay={0.2}>
                <div className="w-12 h-12 bg-purple-50 rounded-xl flex items-center justify-center text-purple-600 mb-4 group-hover:scale-110 transition-transform duration-300">
                    <FileText size={24} />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-purple-600 transition-colors">Importazione AI</h3>
                <p className="text-sm text-gray-500 mb-4">Trascina i tuoi PDF. L'intelligenza artificiale estrarrà dati, date e dipendenti automaticamente.</p>
                <span className="text-sm font-semibold text-purple-600 flex items-center gap-1 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all">
                    Tutorial Import <ArrowRight size={14} />
                </span>
            </GuideCard>
          </Link>

          <Link to="/validation" className="block h-full">
            <GuideCard className="h-full hover:border-orange-300 hover:shadow-lg group" delay={0.3}>
                <div className="w-12 h-12 bg-orange-50 rounded-xl flex items-center justify-center text-orange-600 mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Database size={24} />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-orange-600 transition-colors">Convalida Dati</h3>
                <p className="text-sm text-gray-500 mb-4">Revisiona i dati incerti o orfani prima di confermarli nel database ufficiale aziendale.</p>
                <span className="text-sm font-semibold text-orange-600 flex items-center gap-1 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all">
                    Impara a Validare <ArrowRight size={14} />
                </span>
            </GuideCard>
          </Link>

          <Link to="/calendar" className="block h-full">
            <GuideCard className="h-full hover:border-green-300 hover:shadow-lg group" delay={0.4}>
                <div className="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center text-green-600 mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Calendar size={24} />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-green-600 transition-colors">Scadenzario Grafico</h3>
                <p className="text-sm text-gray-500 mb-4">Visualizza la timeline Gantt delle scadenze e pianifica i rinnovi con mesi di anticipo.</p>
                <span className="text-sm font-semibold text-green-600 flex items-center gap-1 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all">
                    Vedi Gantt <ArrowRight size={14} />
                </span>
            </GuideCard>
          </Link>

          <Link to="/security" className="block h-full">
            <GuideCard className="h-full hover:border-gray-400 hover:shadow-lg group" delay={0.5}>
                <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center text-gray-700 mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Shield size={24} />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-gray-700 transition-colors">Sicurezza & Audit</h3>
                <p className="text-sm text-gray-500 mb-4">Gestione utenti, crittografia database, log di accesso e protezione dei dati sensibili.</p>
                <span className="text-sm font-semibold text-gray-700 flex items-center gap-1 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all">
                    Protocolli <ArrowRight size={14} />
                </span>
            </GuideCard>
          </Link>

          <Link to="/troubleshooting" className="block h-full">
            <GuideCard className="h-full hover:border-red-300 hover:shadow-lg group" delay={0.6}>
                <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center text-red-600 mb-4 group-hover:scale-110 transition-transform duration-300">
                    <LifeBuoy size={24} />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-red-600 transition-colors">Supporto & FAQ</h3>
                <p className="text-sm text-gray-500 mb-4">Hai un problema? Trova soluzioni rapide per errori comuni, licenze e connessioni.</p>
                <span className="text-sm font-semibold text-red-600 flex items-center gap-1 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all">
                    Risolvi Problemi <ArrowRight size={14} />
                </span>
            </GuideCard>
          </Link>
        </div>
      </section>

      {/* Secondary Links */}
      <section className="border-t border-gray-200 pt-10">
        <h3 className="text-xl font-bold text-gray-800 mb-6 px-2">Risorse Utili</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
             <Link to="/maintenance" className="p-4 rounded-lg border border-gray-100 hover:bg-white hover:shadow-md transition-all flex items-center gap-3 text-gray-600 hover:text-blue-700 bg-gray-50/50">
                <HardDrive size={20} /> <span className="font-medium">Backup</span>
             </Link>
             <Link to="/glossary" className="p-4 rounded-lg border border-gray-100 hover:bg-white hover:shadow-md transition-all flex items-center gap-3 text-gray-600 hover:text-blue-700 bg-gray-50/50">
                <Book size={20} /> <span className="font-medium">Glossario</span>
             </Link>
             <Link to="/shortcuts" className="p-4 rounded-lg border border-gray-100 hover:bg-white hover:shadow-md transition-all flex items-center gap-3 text-gray-600 hover:text-blue-700 bg-gray-50/50">
                <Keyboard size={20} /> <span className="font-medium">Hotkeys</span>
             </Link>
             <Link to="/settings" className="p-4 rounded-lg border border-gray-100 hover:bg-white hover:shadow-md transition-all flex items-center gap-3 text-gray-600 hover:text-blue-700 bg-gray-50/50">
                <Zap size={20} /> <span className="font-medium">Opzioni</span>
             </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;
