import React from 'react';
import { motion } from 'framer-motion';
import { LayoutDashboard, FileText, Database, Calendar, ArrowRight, LifeBuoy, Shield, HardDrive, Book, Keyboard } from 'lucide-react';
import { Link } from 'react-router-dom';

const FeatureCard = ({ icon: Icon, title, desc, to, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay }}
    className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md hover:border-intelleo-accent/30 transition-all group cursor-pointer"
  >
    <Link to={to} className="block h-full">
      <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center text-intelleo-accent mb-4 group-hover:bg-intelleo-accent group-hover:text-white transition-colors">
        <Icon size={24} />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-intelleo-accent transition-colors">{title}</h3>
      <p className="text-gray-500 text-sm leading-relaxed mb-4">{desc}</p>
      <div className="flex items-center text-sm font-medium text-intelleo-accent opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0 transition-all">
        Esplora <ArrowRight size={16} className="ml-1" />
      </div>
    </Link>
  </motion.div>
);

const Home = () => {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <span className="inline-block py-1 px-3 rounded-full bg-blue-100 text-blue-800 text-xs font-semibold tracking-wide mb-4">
            GUIDA UFFICIALE 2025
          </span>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Benvenuto in <span className="text-intelleo-accent">Intelleo</span>
          </h1>
          <p className="text-xl text-gray-500 max-w-2xl mx-auto leading-relaxed">
            La suite completa in azienda per la gestione automatizzata delle scadenze sui corsi di formazione e visite mediche
          </p>
        </motion.div>
      </section>

      {/* Feature Grid */}
      <section>
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-bold text-gray-800">Moduli Principali</h2>
          <span className="text-sm text-gray-500">Seleziona un modulo per iniziare il tutorial</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard
            icon={LayoutDashboard}
            title="Dashboard & Database"
            desc="Visualizza lo stato globale delle conformità. Monitora certificati validi, in scadenza e scaduti in un'unica vista."
            to="/dashboard"
            delay={0.1}
          />
          <FeatureCard
            icon={FileText}
            title="Importazione AI"
            desc="Carica i PDF trascinandoli. L'intelligenza artificiale estrarrà automaticamente date, dipendenti e documenti."
            to="/import"
            delay={0.2}
          />
          <FeatureCard
            icon={Database}
            title="Convalida Dati"
            desc="Revisiona e approva i dati estratti dall'AI prima che entrino nel database ufficiale."
            to="/validation"
            delay={0.3}
          />
          <FeatureCard
            icon={Calendar}
            title="Scadenzario Grafico"
            desc="Una timeline visiva (Gantt) per pianificare i rinnovi e vedere le scadenze a colpo d'occhio."
            to="/calendar"
            delay={0.4}
          />
          <FeatureCard
            icon={Shield}
            title="Sicurezza & Audit"
            desc="Dettagli sulla crittografia del database, gestione degli accessi e log delle attività per la compliance."
            to="/security"
            delay={0.5}
          />
          <FeatureCard
            icon={LifeBuoy}
            title="Risoluzione Problemi"
            desc="Hai riscontrato un errore? Consulta le FAQ tecniche per risolvere rapidamente problemi di connessione o licenza."
            to="/troubleshooting"
            delay={0.6}
          />

          {/* New Sections */}
          <FeatureCard
            icon={HardDrive}
            title="Backup & Manutenzione"
            desc="Come proteggere i tuoi dati, eseguire backup manuali e migrare l'installazione su nuovi PC."
            to="/maintenance"
            delay={0.7}
          />
          <FeatureCard
            icon={Book}
            title="Glossario"
            desc="Dizionario dei termini tecnici: Matricola, Orfano, Audit Log e altre definizioni utili."
            to="/glossary"
            delay={0.8}
          />
          <FeatureCard
            icon={Keyboard}
            title="Scorciatoie & Comandi"
            desc="Velocizza il lavoro con le combinazioni di tasti e le funzioni nascoste del mouse."
            to="/shortcuts"
            delay={0.9}
          />
        </div>
      </section>
    </div>
  );
};

export default Home;
