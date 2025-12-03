from datetime import date
from desktop_app.services.license_manager import LicenseManager

APP_KNOWLEDGE = {
    "TABS": {
        "Database": "Visualizza tutti i certificati approvati. Permette di filtrare, esportare e modificare i record. È la vista principale.",
        "Analisi Documenti": "Permette di caricare PDF (trascinandoli o selezionandoli) per l'estrazione automatica dei dati tramite IA.",
        "Convalida Dati": "Mostra i dati estratti dall'IA che richiedono conferma o correzione manuale prima di entrare nel Database.",
        "Scadenzario": "Visualizza un diagramma di Gantt e una timeline delle scadenze. Permette di generare report PDF e inviare email.",
        "Statistiche": "Grafici e metriche sulla conformità aziendale e lo stato dei corsi.",
        "Anagrafica": "Gestione completa dei dipendenti (aggiunta, modifica, importazione CSV).",
        "Configurazione": "Gestione impostazioni (SMTP, API Key, Utenti, Backup, Sicurezza).",
        "Guida Utente": "Manuale interattivo per l'uso del software."
    },
    "FEATURES": {
        "AI Extraction": "Il sistema usa Gemini Pro 2.5 per leggere PDF e identificare automaticamente dipendente, corso e scadenze.",
        "Validazione": "I dati AI non vanno subito nel DB. Devono essere validati dall'utente nella scheda 'Convalida Dati'.",
        "Notifiche": "Il sistema invia alert email automatici per le scadenze imminenti (configurabili).",
        "Sicurezza": "Il database è cifrato. L'accesso è protetto da login. Le azioni sensibili sono loggate nell'Audit Log."
    }
}

def get_dynamic_context(api_client):
    """
    Fetches real-time context data for the AI.
    """
    context = []

    # 1. License Info
    try:
        lic_data = LicenseManager.get_license_data() or {}
        expiry = lic_data.get("Scadenza Licenza", "Sconosciuta")
        hwid = lic_data.get("Hardware ID", "N/A")
        context.append(f"LICENZA: Scade il {expiry}. HWID: {hwid}")
    except Exception:
        context.append("LICENZA: Info non disponibili.")

    # 2. Stats
    try:
        stats = api_client.get_stats_summary()
        # stats = {'total_dipendenti': X, 'total_certificati': Y, 'scaduti': Z, 'in_scadenza': W, ...}

        n_dip = stats.get("total_dipendenti", 0)
        n_cert = stats.get("total_certificati", 0)
        n_scaduti = stats.get("scaduti", 0)
        n_imminent = stats.get("in_scadenza", 0)
        compliance = stats.get("compliance_percent", 0)

        context.append(f"STATISTICHE: {n_dip} Dipendenti, {n_cert} Certificati.")
        context.append(f"SCADENZE: {n_scaduti} Scaduti, {n_imminent} In scadenza.")
        context.append(f"COMPLIANCE AZIENDALE: {compliance}%")

    except Exception as e:
        context.append(f"STATISTICHE: Errore nel recupero dati ({str(e)})")

    return "\n".join(context)
