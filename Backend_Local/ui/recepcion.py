from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QPushButton, QDialog, QTextEdit, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
import database

class DetalleRegistroDialog(QDialog):
    """Ventana modal rediseñada con estilo SaaS Moderno."""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Ficha de Cliente - {data['nombre']}")
        self.setMinimumSize(500, 580)
        self.setStyleSheet("background-color: #0B0E14; color: #F0F6FC;")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(18)
        
        title = QLabel("📄 Ficha Técnica de Recepción")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #58A6FF;")
        lay.addWidget(title)
        
        # Info Card
        info_frame = QFrame()
        info_frame.setObjectName("card")
        info_frame.setStyleSheet("""
            QFrame#card {
                background: #161B22; 
                border-radius: 12px; 
                border: 1px solid #30363D;
                padding: 15px;
            }
        """)
        info_lay = QVBoxLayout(info_frame)
        info_lay.setSpacing(10)
        
        def add_field(label, value):
            container = QWidget()
            h_lay = QHBoxLayout(container)
            h_lay.setContentsMargins(0,0,0,0)
            
            lbl_key = QLabel(f"{label}:")
            lbl_key.setStyleSheet("color: #8B949E; font-weight: bold; font-size: 13px; border:none;")
            lbl_key.setFixedWidth(100)
            
            lbl_val = QLabel(str(value))
            lbl_val.setStyleSheet("color: #F0F6FC; font-size: 14px; border:none;")
            lbl_val.setWordWrap(True)
            
            h_lay.addWidget(lbl_key)
            h_lay.addWidget(lbl_val, 1)
            info_lay.addWidget(container)
            
        add_field("CLIENTE", data.get('nombre', 'N/A'))
        add_field("CÉDULA", data.get('ci', 'N/A'))
        add_field("TELÉFONO", data.get('telefono', 'N/A'))
        add_field("FECHA", data.get('fecha', 'N/A'))
        add_field("EQUIPO", data.get('equipo', 'N/A'))
        add_field("SERIAL", data.get('serial', 'S/N'))
        
        lay.addWidget(info_frame)
        
        # Falla / Motivo
        lbl_motivo = QLabel("MOTIVO / FALLA REPORTADA")
        lbl_motivo.setStyleSheet("color: #8B949E; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        lay.addWidget(lbl_motivo)
        
        self.txt_falla = QTextEdit()
        self.txt_falla.setReadOnly(True)
        falla_det = data.get('falla') or "Sin descripción técnica proporcionada."
        self.txt_falla.setPlainText(falla_det)
        self.txt_falla.setStyleSheet("""
            QTextEdit {
                background-color: #0D1117; 
                border: 1px solid #30363D;
                border-radius: 8px; 
                padding: 15px; 
                font-size: 14px; 
                color: #3FB950;
            }
        """)
        lay.addWidget(self.txt_falla)
        
        btn_close = QPushButton("Entendido")
        btn_close.clicked.connect(self.close)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #21262D; color: #C9D1D9; border: 1px solid #363B42;
                padding: 12px; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #30363D; color: #F0F6FC; }
        """)
        lay.addWidget(btn_close)

class RecepcionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        
        self.refresh_timer = QTimer()
        self.refresh_timer.setInterval(10000) 
        self.refresh_timer.timeout.connect(self._auto_sync)
        self.refresh_timer.start()
        
        self._refresh_table()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        # Header
        hdr = QHBoxLayout()
        self.lbl_title = QLabel("📥 Recepción de Equipos Cloud")
        self.lbl_title.setStyleSheet("color: #F0F6FC; font-size: 26px; font-weight: bold; letter-spacing: -0.5px;")
        hdr.addWidget(self.lbl_title)
        hdr.addStretch()
        
        btn_sync = QPushButton("🔄 Sincronizar")
        btn_sync.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sync.clicked.connect(self._sync_now)
        btn_sync.setStyleSheet("""
            QPushButton {
                background: #238636; color: white; border: 1px solid #2ea043;
                padding: 10px 24px; border-radius: 8px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background: #2ea043; }
        """)
        hdr.addWidget(btn_sync)
        layout.addLayout(hdr)

        # Modern Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["FECHA", "CLIENTE", "CÉDULA", "EQUIPO", "ESTADO / FALLA"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        
        # Aplicamos el estilo SaaS a la tabla
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False) # Quita las líneas de rejilla
        self.table.itemDoubleClicked.connect(self._show_details)
        
        layout.addWidget(self.table)

        # Hint
        lbl_hint = QLabel("💡 Doble clic para ver la ficha técnica completa del equipo.")
        lbl_hint.setStyleSheet("color: #484F58; font-size: 13px; font-style: italic;")
        layout.addWidget(lbl_hint)

    def _refresh_table(self):
        self.registros = database.get_new_cloud_registrations()
        self.table.setRowCount(len(self.registros))
        
        for row, reg in enumerate(self.registros):
            # Formatear items con estilo
            f_item = QTableWidgetItem(reg['fecha'])
            n_item = QTableWidgetItem(reg['nombre'])
            c_item = QTableWidgetItem(reg['ci'])
            e_item = QTableWidgetItem(reg['equipo'])
            
            falla_txt = reg.get('falla') or "Sin descripción"
            if len(falla_txt) > 50: 
                falla_txt = falla_txt[:47] + "..."
            
            fa_item = QTableWidgetItem(falla_txt)
            fa_item.setForeground(Qt.GlobalColor.gray)
            
            self.table.setItem(row, 0, f_item)
            self.table.setItem(row, 1, n_item)
            self.table.setItem(row, 2, c_item)
            self.table.setItem(row, 3, e_item)
            self.table.setItem(row, 4, fa_item)

    def _auto_sync(self):
        count = database.sincronizar_nube()
        if count > 0:
            self._refresh_table()
            self.lbl_title.setText(f"📥 ¡NUEVOS EQUIPOS! (+{count})")
            self.lbl_title.setStyleSheet("color: #3FB950; font-size: 26px; font-weight: bold;")
            QTimer.singleShot(5000, self._reset_title)

    def _sync_now(self):
        count = database.sincronizar_nube()
        self._refresh_table()
        if count > 0:
            QMessageBox.information(self, "Cloud Sync", f"Se han importado {count} nuevos equipos con éxito.")
        else:
            QMessageBox.information(self, "Cloud Sync", "El sistema está actualizado. No hay nuevos registros.")

    def _show_details(self, item):
        row = item.row()
        if row < len(self.registros):
            data = self.registros[row]
            dlg = DetalleRegistroDialog(data, self)
            dlg.exec()

    def _reset_title(self):
        self.lbl_title.setText("📥 Recepción de Equipos Cloud")
        self.lbl_title.setStyleSheet("color: #F0F6FC; font-size: 26px; font-weight: bold;")
