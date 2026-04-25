from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
import database

class ClientesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300)
        self.search_timer.timeout.connect(self._refresh_data)
        
        self.cloud_timer = QTimer()
        self.cloud_timer.setInterval(10000) # Cada 10 segundos
        self.cloud_timer.timeout.connect(self._sync_cloud)
        self.cloud_timer.start()
        
        self._setup_ui()
        self._refresh_data()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(20)

        # Header
        hdr = QHBoxLayout()
        self.lbl_title = QLabel("👥 Gestión de Clientes")
        self.lbl_title.setStyleSheet("color: #e2e8f0; font-size: 22px; font-weight: bold;")
        hdr.addWidget(self.lbl_title)
        hdr.addStretch()

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Buscar por nombre o C.I...")
        self.txt_search.setFixedWidth(300)
        self.txt_search.setFixedHeight(40)
        self.txt_search.setStyleSheet("""
            QLineEdit {
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                color: white;
                padding-left: 10px;
            }
            QLineEdit:focus { border-color: #3b82f6; }
        """)
        self.txt_search.textChanged.connect(self.search_timer.start)
        hdr.addWidget(self.txt_search)
        lay.addLayout(hdr)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Cédula / RIF", "Nombre Completo", "Teléfono", "Acciones"])
        
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        
        self.table.setColumnWidth(0, 140)
        self.table.setColumnWidth(2, 160)
        self.table.setColumnWidth(3, 100)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        lay.addWidget(self.table)

    def _refresh_data(self):
        query = self.txt_search.text().strip().lower()
        clientes = database.get_all_clientes() # Returns list of (ci, nombre, telefono)
        
        # Filter if search query exists
        if query:
            clientes = [c for c in clientes if query in c[0].lower() or query in c[1].lower()]
            
        self.table.setRowCount(len(clientes))
        for row, (ci, nombre, tlf) in enumerate(clientes):
            c_item = QTableWidgetItem(ci)
            c_item.setForeground(QColor("#10B981"))
            c_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            
            self.table.setItem(row, 0, c_item)
            self.table.setItem(row, 1, QTableWidgetItem(nombre))
            self.table.setItem(row, 2, QTableWidgetItem(tlf))
            
            btn_wa = QPushButton("📲 WA")
            btn_wa.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_wa.setStyleSheet("""
                QPushButton {
                    background: #059669;
                    color: white;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-weight: bold;
                }
                QPushButton:hover { background: #10b981; }
            """)
            btn_wa.clicked.connect(lambda _, p=tlf, n=nombre: self._open_whatsapp(p, n))
            
            self.table.setCellWidget(row, 3, self._wrap(btn_wa))
            self.table.setRowHeight(row, 45)

    def _sync_cloud(self):
        new_count = database.sync_cloud_registrations()
        if new_count > 0:
            # Si hay nuevos registros, refrescamos la tabla
            self._refresh_data()
            # Opcional: mostrar una notificación discreta o cambiar color del título
            self.lbl_title.setText(f"👥 Gestión de Clientes ({new_count} nuevos!)")
            self.lbl_title.setStyleSheet("color: #10b981; font-size: 22px; font-weight: bold;")
            QTimer.singleShot(5000, self._reset_title)

    def _reset_title(self):
        self.lbl_title.setText("👥 Gestión de Clientes")
        self.lbl_title.setStyleSheet("color: #e2e8f0; font-size: 22px; font-weight: bold;")

    def _wrap(self, btn):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(5, 5, 5, 5)
        l.addWidget(btn)
        return w

    def _open_whatsapp(self, phone, name):
        if not phone: return
        clean_phone = "".join(filter(str.isdigit, phone))
        if len(clean_phone) == 10 and clean_phone.startswith('4'): clean_phone = "58" + clean_phone
        elif len(clean_phone) == 11 and clean_phone.startswith('0'): clean_phone = "58" + clean_phone[1:]
        
        import urllib.parse
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        msg = f"Hola *{name}*, le contactamos de *Llanos Core*."
        url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={urllib.parse.quote(msg)}"
        QDesktopServices.openUrl(QUrl(url))
