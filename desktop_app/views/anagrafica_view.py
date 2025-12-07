from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QStackedWidget,
    QFormLayout, QMessageBox, QTabWidget, QTableView, QHeaderView,
    QDateEdit, QComboBox, QDialog, QAbstractItemView, QGridLayout
)
from PyQt6.QtCore import Qt, QSize, QDate, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QStandardItemModel, QStandardItem
from datetime import datetime
from desktop_app.api_client import APIClient
from desktop_app.constants import STYLE_QFRAME_CARD

class KPIStatWidget(QFrame):
    def __init__(self, title, value, color="#3B82F6", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #6B7280; font-size: 12px; font-weight: 600; border: none;")
        layout.addWidget(lbl_title)

        self.lbl_value = QLabel(str(value))
        self.lbl_value.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 800; border: none;")
        layout.addWidget(self.lbl_value)

    def set_value(self, value):
        self.lbl_value.setText(str(value))

class AnagraficaView(QWidget):
    data_changed = pyqtSignal()

    def __init__(self, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.all_employees = [] # List of dicts
        self.current_employee_id = None
        self.is_read_only = False # Should be set from main window usually

        self.setup_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- LEFT PANEL: List ---
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        # S1192: Use constant
        left_panel.setStyleSheet(STYLE_QFRAME_CARD)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(10)

        # Search
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cerca dipendente...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background-color: #F9FAFB;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_list)
        left_layout.addWidget(self.search_bar)

        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.setFrameShape(QFrame.Shape.NoFrame)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F3F4F6;
                color: #1F2937;
            }
            QListWidget::item:selected {
                background-color: #EFF6FF;
                color: #1D4ED8;
                border-radius: 6px;
                border-bottom: none;
            }
        """)
        self.list_widget.itemClicked.connect(self.on_employee_selected)
        left_layout.addWidget(self.list_widget)

        # Add Button
        self.btn_add = QPushButton("+ Nuovo Dipendente")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #1D4ED8;
                color: white;
                font-weight: 600;
                padding: 10px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
        """)
        self.btn_add.clicked.connect(self.show_create_form)
        left_layout.addWidget(self.btn_add)

        main_layout.addWidget(left_panel)

        # --- RIGHT PANEL: Stacked (Empty, Detail, Form) ---
        self.right_stack = QStackedWidget()

        # Page 0: Empty State
        self.page_empty = QWidget()
        empty_layout = QVBoxLayout(self.page_empty)
        empty_lbl = QLabel("Seleziona un dipendente dalla lista o creane uno nuovo.")
        empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_lbl.setStyleSheet("color: #9CA3AF; font-size: 16px;")
        empty_layout.addWidget(empty_lbl)
        self.right_stack.addWidget(self.page_empty)

        # Page 1: Detail View
        self.page_detail = QWidget()
        self.setup_detail_page()
        self.right_stack.addWidget(self.page_detail)

        # Page 2: Edit/Create Form
        self.page_form = QWidget()
        self.setup_form_page()
        self.right_stack.addWidget(self.page_form)

        main_layout.addWidget(self.right_stack)
        main_layout.setStretch(1, 1) # Expand right panel

    def setup_detail_page(self):
        layout = QVBoxLayout(self.page_detail)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header Card
        self.header_card = QFrame()
        self.header_card.setStyleSheet(STYLE_QFRAME_CARD)
        header_layout = QHBoxLayout(self.header_card)
        header_layout.setContentsMargins(20, 20, 20, 20)

        # Avatar Placeholder (Circle)
        avatar = QLabel("👤")
        avatar.setFixedSize(60, 60)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # S3457: Fixed f-string usage or simple string
        avatar.setStyleSheet("""
            background-color: #EFF6FF;
            color: #1D4ED8;
            font-size: 30px;
            border-radius: 30px;
            border: 1px solid #BFDBFE;
        """)
        header_layout.addWidget(avatar)

        # Info
        info_layout = QVBoxLayout()
        self.lbl_name = QLabel("Nome Cognome")
        self.lbl_name.setStyleSheet("font-size: 20px; font-weight: 800; color: #111827; border: none;")
        self.lbl_matricola = QLabel("Matricola: 12345")
        self.lbl_matricola.setStyleSheet("font-size: 14px; color: #6B7280; border: none;")
        self.lbl_dept = QLabel("Reparto: Produzione")
        self.lbl_dept.setStyleSheet("font-size: 14px; color: #6B7280; border: none;")

        info_layout.addWidget(self.lbl_name)
        info_layout.addWidget(self.lbl_matricola)
        info_layout.addWidget(self.lbl_dept)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()

        # Action Buttons
        btn_layout = QVBoxLayout()
        self.btn_edit = QPushButton("Modifica")
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #D1D5DB;
                color: #374151;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #F3F4F6; }
        """)
        self.btn_edit.clicked.connect(self.start_edit_mode)

        self.btn_delete = QPushButton("Elimina")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #EF4444;
                color: #EF4444;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #FEF2F2; }
        """)
        self.btn_delete.clicked.connect(self.delete_current_employee)

        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        header_layout.addLayout(btn_layout)

        layout.addWidget(self.header_card)

        # KPI Grid
        kpi_container = QWidget()
        kpi_layout = QHBoxLayout(kpi_container)
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        kpi_layout.setSpacing(15)

        self.kpi_total = KPIStatWidget("CERTIFICATI TOTALI", "0", "#3B82F6")
        self.kpi_valid = KPIStatWidget("VALIDI", "0", "#10B981")
        self.kpi_expiring = KPIStatWidget("IN SCADENZA", "0", "#F59E0B")
        self.kpi_expired = KPIStatWidget("SCADUTI", "0", "#EF4444")

        kpi_layout.addWidget(self.kpi_total)
        kpi_layout.addWidget(self.kpi_valid)
        kpi_layout.addWidget(self.kpi_expiring)
        kpi_layout.addWidget(self.kpi_expired)

        layout.addWidget(kpi_container)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #E5E7EB; border-radius: 8px; background: white; }
            QTabBar::tab {
                background: #F3F4F6;
                color: #6B7280;
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { background: white; color: #1D4ED8; font-weight: 600; border-bottom: 2px solid #1D4ED8; }
        """)

        # Tab 1: Certificati
        self.tab_certs = QWidget()
        certs_layout = QVBoxLayout(self.tab_certs)
        self.table_certs = QTableView()
        self.table_certs.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_certs.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_certs.setAlternatingRowColors(True)
        self.table_certs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_certs.setStyleSheet("""
            QTableView {
                border: none;
                gridline-color: #F3F4F6;
                selection-background-color: #EFF6FF;
                selection-color: #1F2937;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                padding: 8px;
                border: none;
                font-weight: 600;
                color: #374151;
            }
        """)
        certs_layout.addWidget(self.table_certs)
        self.tabs.addTab(self.tab_certs, "Certificati")

        # Tab 2: Dettagli Estesi
        self.tab_info = QWidget()
        info_tab_layout = QFormLayout(self.tab_info)
        info_tab_layout.setContentsMargins(20, 20, 20, 20)
        info_tab_layout.setSpacing(15)

        self.detail_lbl_email = QLabel("-")
        self.detail_lbl_assunzione = QLabel("-")
        self.detail_lbl_nascita = QLabel("-")

        info_tab_layout.addRow(QLabel("Email:"), self.detail_lbl_email)
        info_tab_layout.addRow(QLabel("Data Assunzione:"), self.detail_lbl_assunzione)
        info_tab_layout.addRow(QLabel("Data Nascita:"), self.detail_lbl_nascita)

        self.tabs.addTab(self.tab_info, "Dati Personali")

        layout.addWidget(self.tabs)

    def setup_form_page(self):
        # Create/Edit Form
        self.form_container = QFrame()
        self.form_container.setStyleSheet(STYLE_QFRAME_CARD)
        outer_layout = QVBoxLayout(self.page_form)
        outer_layout.addWidget(self.form_container)
        outer_layout.addStretch() # Push up

        layout = QFormLayout(self.form_container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Modifica Dipendente")
        title.setObjectName("form_title")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #111827; border: none; margin-bottom: 20px;")
        layout.addRow(title)

        self.inp_nome = QLineEdit()
        self.inp_cognome = QLineEdit()
        self.inp_matricola = QLineEdit()
        self.inp_email = QLineEdit()
        self.inp_reparto = QLineEdit() # Could be ComboBox if we had a list
        self.inp_nascita = QDateEdit()
        self.inp_nascita.setDisplayFormat("dd/MM/yyyy")
        self.inp_nascita.setCalendarPopup(True)
        # Support for nullable dates: set min date to 1900 and special text
        min_date = QDate(1900, 1, 1)
        self.inp_nascita.setMinimumDate(min_date)
        self.inp_nascita.setSpecialValueText(" ")

        self.inp_assunzione = QDateEdit()
        self.inp_assunzione.setDisplayFormat("dd/MM/yyyy")
        self.inp_assunzione.setCalendarPopup(True)
        self.inp_assunzione.setMinimumDate(min_date)
        self.inp_assunzione.setSpecialValueText(" ")

        self.inp_matricola.setPlaceholderText("Es. 12345")
        self.inp_email.setPlaceholderText("email@azienda.it")

        layout.addRow("Nome:", self.inp_nome)
        layout.addRow("Cognome:", self.inp_cognome)
        layout.addRow("Matricola:", self.inp_matricola)
        layout.addRow("Email:", self.inp_email)
        layout.addRow("Reparto:", self.inp_reparto)
        layout.addRow("Data Nascita:", self.inp_nascita)
        layout.addRow("Data Assunzione:", self.inp_assunzione)

        btn_box = QHBoxLayout()
        self.btn_save = QPushButton("Salva")
        self.btn_save.setStyleSheet("background-color: #1D4ED8; color: white; padding: 8px 16px; border-radius: 6px; font-weight: 600;")
        self.btn_save.clicked.connect(self.save_employee)

        self.btn_cancel = QPushButton("Annulla")
        self.btn_cancel.setStyleSheet("background-color: white; border: 1px solid #D1D5DB; color: #374151; padding: 8px 16px; border-radius: 6px; font-weight: 600;")
        self.btn_cancel.clicked.connect(self.cancel_edit)

        btn_box.addWidget(self.btn_cancel)
        btn_box.addWidget(self.btn_save)
        layout.addRow(btn_box)

    def refresh_data(self):
        """Loads the list of employees."""
        try:
            data = self.api_client.get_dipendenti_list()
            self.all_employees = sorted(data, key=lambda x: f"{x['cognome']} {x['nome']}")
            self.filter_list("")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore caricamento dipendenti: {e}")

    def filter_list(self, text):
        search = self.search_bar.text().lower()
        self.list_widget.clear()

        for emp in self.all_employees:
            full_name = f"{emp['cognome']} {emp['nome']}"
            if search in full_name.lower() or (emp['matricola'] and search in emp['matricola'].lower()):
                item = QListWidgetItem(full_name)
                item.setData(Qt.ItemDataRole.UserRole, emp['id'])
                # Subtitle (Matricola)
                matr = emp['matricola'] or "N/A"
                item.setToolTip(f"Matricola: {matr}")
                self.list_widget.addItem(item)

    def on_employee_selected(self, item):
        emp_id = item.data(Qt.ItemDataRole.UserRole)
        self.load_employee_detail(emp_id)

    def load_employee_detail(self, emp_id):
        try:
            data = self.api_client.get_dipendente_detail(emp_id)
            self.current_employee_id = emp_id
            self.populate_detail(data)
            self.right_stack.setCurrentWidget(self.page_detail)
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile caricare dettagli: {e}")

    def populate_detail(self, data):
        # S3776: Refactored logic to reduce complexity? Already quite split.
        # Header
        full_name = f"{data['cognome']} {data['nome']}"
        self.lbl_name.setText(full_name)
        self.lbl_matricola.setText(f"Matricola: {data['matricola'] or 'N/A'}")
        self.lbl_dept.setText(f"Reparto: {data['categoria_reparto'] or 'Non assegnato'}")

        # Info Tab
        self.detail_lbl_email.setText(data.get('email') or "-")
        assunzione = data.get('data_assunzione')
        if assunzione:
            self.detail_lbl_assunzione.setText(datetime.strptime(assunzione, '%Y-%m-%d').strftime('%d/%m/%Y'))
        else:
            self.detail_lbl_assunzione.setText("-")

        nascita = data.get('data_nascita')
        if nascita:
            self.detail_lbl_nascita.setText(datetime.strptime(nascita, '%Y-%m-%d').strftime('%d/%m/%Y'))
        else:
            self.detail_lbl_nascita.setText("-")

        self._populate_certs_table(data.get('certificati', []))

    def _populate_certs_table(self, certs):
        total = len(certs)
        valid = 0
        expiring = 0
        expired = 0

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Corso", "Categoria", "Emissione", "Scadenza", "Stato"])

        for cert in certs:
            stato = cert['stato_certificato']
            if stato == 'attivo': valid += 1
            elif stato == 'in_scadenza': expiring += 1
            elif stato == 'scaduto': expired += 1

            row = [
                QStandardItem(cert['corso']),
                QStandardItem(cert['categoria']),
                QStandardItem(cert['data_rilascio']),
                QStandardItem(cert['data_scadenza'] or "-"),
                QStandardItem(cert['stato_certificato'].replace("_", " ").title())
            ]

            color = QColor("black")
            if stato == 'attivo': color = QColor("#10B981")
            elif stato == 'in_scadenza': color = QColor("#F59E0B")
            elif stato == 'scaduto': color = QColor("#EF4444")

            row[4].setForeground(color)
            model.appendRow(row)

        self.table_certs.setModel(model)

        self.kpi_total.set_value(total)
        self.kpi_valid.set_value(valid)
        self.kpi_expiring.set_value(expiring)
        self.kpi_expired.set_value(expired)

    def show_create_form(self):
        self.current_employee_id = None
        self.findChild(QLabel, "form_title").setText("Nuovo Dipendente")
        self.inp_nome.clear()
        self.inp_cognome.clear()
        self.inp_matricola.clear()
        self.inp_email.clear()
        self.inp_reparto.clear()
        self.inp_nascita.setDate(QDate.currentDate())
        self.inp_assunzione.setDate(QDate.currentDate()) # Should technically be empty/special
        self.right_stack.setCurrentWidget(self.page_form)

    def start_edit_mode(self):
        if not self.current_employee_id: return

        # Fetch fresh data or use displayed? Fetch fresh is safer.
        try:
            data = self.api_client.get_dipendente_detail(self.current_employee_id)
            self.populate_form(data)
            self.findChild(QLabel, "form_title").setText("Modifica Dipendente")
            self.right_stack.setCurrentWidget(self.page_form)
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

    def populate_form(self, data):
        self.inp_nome.setText(data['nome'])
        self.inp_cognome.setText(data['cognome'])
        self.inp_matricola.setText(data['matricola'] or "")
        self.inp_email.setText(data.get('email') or "")
        self.inp_reparto.setText(data.get('categoria_reparto') or "")

        min_date = QDate(1900, 1, 1)
        if data.get('data_nascita'):
            self.inp_nascita.setDate(QDate.fromString(data['data_nascita'], "yyyy-MM-dd"))
        else:
            self.inp_nascita.setDate(min_date)

        if data.get('data_assunzione'):
            self.inp_assunzione.setDate(QDate.fromString(data['data_assunzione'], "yyyy-MM-dd"))
        else:
             self.inp_assunzione.setDate(min_date)

    def save_employee(self):
        min_date = QDate(1900, 1, 1)

        nascita = self.inp_nascita.date()
        assunzione = self.inp_assunzione.date()

        data = {
            "nome": self.inp_nome.text().strip(),
            "cognome": self.inp_cognome.text().strip(),
            "matricola": self.inp_matricola.text().strip() or None,
            "email": self.inp_email.text().strip() or None,
            "categoria_reparto": self.inp_reparto.text().strip() or None,
            "data_nascita": nascita.toString("yyyy-MM-dd") if nascita > min_date else None,
            "data_assunzione": assunzione.toString("yyyy-MM-dd") if assunzione > min_date else None
        }

        if not data["nome"] or not data["cognome"]:
            QMessageBox.warning(self, "Attenzione", "Nome e Cognome sono obbligatori.")
            return

        try:
            if self.current_employee_id:
                self.api_client.update_dipendente(self.current_employee_id, data)
                QMessageBox.information(self, "Successo", "Dipendente aggiornato.")
                self.refresh_data()
                self.load_employee_detail(self.current_employee_id) # Go back to detail
                self.data_changed.emit()
            else:
                new_emp = self.api_client.create_dipendente(data)
                QMessageBox.information(self, "Successo", "Dipendente creato.")
                self.refresh_data()
                self.load_employee_detail(new_emp['id'])
                self.data_changed.emit()

        except Exception as e:
            # Handle API errors (e.g. 400 Bad Request for duplicates)
            msg = str(e)
            if "400" in msg and "Matricola" in msg:
                msg = "Matricola già esistente."
            QMessageBox.critical(self, "Errore", f"Salvataggio fallito: {msg}")

    def cancel_edit(self):
        if self.current_employee_id:
            self.right_stack.setCurrentWidget(self.page_detail)
        else:
            self.right_stack.setCurrentWidget(self.page_empty)

    def delete_current_employee(self):
        if not self.current_employee_id: return

        reply = QMessageBox.question(self, "Conferma Eliminazione",
                                     "Sei sicuro di voler eliminare questo dipendente? I certificati diventeranno 'orfani'.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_dipendente(self.current_employee_id)
                self.refresh_data()
                self.right_stack.setCurrentWidget(self.page_empty)
                self.current_employee_id = None
                self.data_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Eliminazione fallita: {e}")
