
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QDialogButtonBox

class GuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Guida Utente")
        self.layout = QVBoxLayout(self)
        self.setMinimumSize(800, 600)

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.layout.addWidget(self.text_browser)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.button_box.accepted.connect(self.accept)
        self.layout.addWidget(self.button_box)

        self.set_guide_content()

    def set_guide_content(self):
        guide_html = """
            <h1>Guida Utente di CertiSync AI</h1>
            <p>Benvenuto nella guida utente di CertiSync AI. Questa guida ti aiuterà a comprendere le funzionalità principali dell'applicazione.</p>

            <h2>Navigazione</h2>
            <p>Usa la barra di navigazione a sinistra per spostarti tra le diverse sezioni dell'applicazione:</p>
            <ul>
                <li><b>Analizza:</b> Carica e analizza i tuoi file PDF per estrarre le informazioni sui certificati.</li>
                <li><b>Convalida Dati:</b> Controlla e valida i dati estratti dall'IA prima di salvarli nel database.</li>
                <li><b>Database:</b> Visualizza, cerca e gestisci tutti i certificati salvati.</li>
                <li><b>Addestra:</b> Migliora le performance del modello di intelligenza artificiale.</li>
            </ul>

            <h2>Come Iniziare</h2>
            <ol>
                <li>Vai alla sezione <b>Analizza</b>.</li>
                <li>Trascina una cartella contenente i tuoi file PDF nell'area designata o clicca sul pulsante per selezionarla.</li>
                <li>L'applicazione analizzerà automaticamente i file e mostrerà i risultati.</li>
                <li>Vai alla sezione <b>Convalida Dati</b> per approvare o correggere le informazioni estratte.</li>
                <li>Una volta convalidati, i certificati saranno disponibili nel <b>Database</b>.</li>
            </ol>

            <h2>Supporto</h2>
            <p>Per qualsiasi domanda o problema, puoi contattare il supporto tramite il menu <b>Supporto > Contatti</b>.</p>
        """
        self.text_browser.setHtml(guide_html)
