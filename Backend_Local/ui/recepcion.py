from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QPushButton, QDialog, QTextEdit, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
import database

class DetalleRegistroDialog(QDialog):
    """Ventana modal para ver los detalles completos de un registro."""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detalles de Recepción - {data['nombre']}")
        self.setMinimumSize(500, 550)
        self.setStyleSheet("background-color: #0f172a; color: #f8fafc;")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(25, 25, 25, 25)
        lay.setSpacing(15)
        
        title = QLabel("📄 Ficha de Recepción")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #10b981;")
        lay.addWidget(title)
        
        # Info Card
        info_frame = QFrame()
        info_frame.setStyleSheet("background: #1e293b; border-radius: 10px; padding: 15px;")
        info_lay = QVBoxLayout(info_frame)
        
        def add_field(label, value):
            lbl = QLabel(f"<b>{label}:</b> {value}")
            lbl.setStyleSheet("font-size: 14px; color: #e2e8f0; border: none;")
            lbl.setWordWrap(True)
            info_lay.addWidget(lbl)
            
        add_field("Cliente", data['nombre'])
        add_field("Cédula/RIF", data['ci'])
        add_field("Teléfono", data['telefono'])
        add_field("Fecha", data['fecha'])
        add_field("Equipo", data['equipo'])
        add_field("Serial", data.get('serial', 'S/N'))
        
        lay.addWidget(info_frame)
        
        # Falla / Motivo
        lay.addWidget(QLabel("<b>MOTIVO / FALLA REPORTADA:</b>"))
        self.txt_falla = QTextEdit()
        self.txt_falla.setReadOnly(True)
        self.txt_falla.setPlainText(data['falla'])
        self.txt_falla.setStyleSheet("""
            QTextEdit {
                background-color: #000; border: 1px solid #334155;
                border-radius: 8px; padding: 15px; font-size: 15px; color: #10b981;
            }
        """)
        lay.addWidget(self.txt_falla)
        
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.close)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #334155; color: white; border: none;
                padding: 12px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #475569; }
        """)
        lay.addWidget(btn_close)

class RecepcionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        
        # Timer de sincronización automática
        self.refresh_timer = QTimer()
        self.refresh_timer.setInterval(10000) # Cada 10 segundos
        self.refresh_timer.timeout.connect(self._auto_sync)
        self.refresh_timer.start()
        
        self._refresh_table()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        hdr = QHBoxLayout()
        self.lbl_title = QLabel("📥 Recepción de Equipos (Nube)")
        self.lbl_title.setStyleSheet("color: #e2e8f0; font-size: 24px; font-weight: bold;")
        hdr.addWidget(self.lbl_title)
        hdr.addStretch()
        
        btn_sync = QPushButton("🔄 Sincronizar Ahora")
        btn_sync.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sync.clicked.connect(self._sync_now)
        btn_sync.setStyleSheet("""
            QPushButton {
                background: #334155; color: white; border: none;
                padding: 10px 20px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #475569; }
        """)
        hdr.addWidget(btn_sync)
        layout.addLayout(hdr)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Fecha", "Cliente", "Cédula", "Equipo", "Falla / Motivo"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e293b; color: #f8fafc;
                gridline-color: #334155; border: 1px solid #334155;
                border-radius: 12px; font-size: 14px;
            }
            QHeaderView::section {
                background-color: #0f172a; color: #94a3b8;
                padding: 12px; border: none; font-weight: bold;
            }
        """)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemDoubleClicked.connect(self._show_details)
        layout.addWidget(self.table)

        # Hint
        lbl_hint = QLabel("💡 Haz doble clic en una fila para ver todos los detalles del equipo.")
        lbl_hint.setStyleSheet("color: #64748b; font-size: 13px; font-style: italic;")
        layout.addWidget(lbl_hint)

    def _refresh_table(self):
        self.registros = database.get_new_cloud_registrations()
        self.table.setRowCount(len(self.registros))
        
        for row, reg in enumerate(self.registros):
            self.table.setItem(row, 0, QTableWidgetItem(reg['fecha']))
            self.table.setItem(row, 1, QTableWidgetItem(reg['nombre']))
            self.table.setItem(row, 2, QTableWidgetItem(reg['ci']))
            self.table.setItem(row, 3, QTableWidgetItem(reg['equipo']))
            
            falla_item = QTableWidgetItem(reg['falla'])
            falla_item.setToolTip("Doble clic para ver detalle completo")
            self.table.setItem(row, 4, falla_item)

    def _auto_sync(self):
        """Sincroniza en segundo plano y avisa si hay novedades."""
        count = database.sincronizar_nube()
        if count > 0:
            self._refresh_table()
            # Aviso visual en el título
            self.lbl_title.setText(f"📥 ¡NUEVO REGISTRO RECIBIDO! (+{count})")
            self.lbl_title.setStyleSheet("color: #10b981; font-size: 24px; font-weight: bold;")
            
            # Notificación tipo Toast (opcional, usamos un message box para que no se le pase al usuario)
            msg = QMessageBox(self)
            msg.setWindowTitle("Llanos Core - Notificación")
            msg.setText(f"🔔 Se han recibido {count} nuevo(s) registro(s) de clientes desde la nube.")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.show()
            QTimer.singleShot(5000, self._reset_title)

    def _sync_now(self):
        count = database.sincronizar_nube()
        self._refresh_table()
        if count > 0:
            QMessageBox.information(self, "Sincronización", f"Se importaron {count} nuevos registros.")
        else:
            QMessageBox.information(self, "Sincronización", "No hay registros nuevos en la nube.")

    def _show_details(self, item):
        row = item.row()
        if row < len(self.registros):
            data = self.registros[row]
            dlg = DetalleRegistroDialog(data, self)
            dlg.exec()

    def _reset_title(self):
        self.lbl_title.setText("📥 Recepción de Equipos (Nube)")
        self.lbl_title.setStyleSheet("color: #e2e8f0; font-size: 24px; font-weight: bold;")
