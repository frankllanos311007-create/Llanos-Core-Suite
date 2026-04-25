from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QPushButton)
from PyQt6.QtCore import Qt, QTimer
import database

class RecepcionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.refresh_timer = QTimer()
        self.refresh_timer.setInterval(10000) # 10 segundos
        self.refresh_timer.timeout.connect(self._refresh_data)
        self.refresh_timer.start()
        
        self._setup_ui()
        self._refresh_data()

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
        layout.addWidget(self.table)

        # Hint
        lbl_hint = QLabel("💡 Los registros nuevos aparecen aquí automáticamente en tiempo real.")
        lbl_hint.setStyleSheet("color: #64748b; font-size: 13px; font-style: italic;")
        layout.addWidget(lbl_hint)

    def _refresh_data(self):
        registros = database.get_new_cloud_registrations()
        self.table.setRowCount(len(registros))
        
        for row, reg in enumerate(registros):
            self.table.setItem(row, 0, QTableWidgetItem(reg['fecha']))
            self.table.setItem(row, 1, QTableWidgetItem(reg['nombre']))
            self.table.setItem(row, 2, QTableWidgetItem(reg['ci']))
            self.table.setItem(row, 3, QTableWidgetItem(reg['equipo']))
            
            falla_item = QTableWidgetItem(reg['falla'])
            falla_item.setToolTip(reg['falla'])
            self.table.setItem(row, 4, falla_item)
            
            for col in range(5):
                self.table.item(row, col).setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

    def _sync_now(self):
        count = database.sincronizar_nube()
        self._refresh_data()
        if count > 0:
            self.lbl_title.setText(f"📥 Recepción de Equipos (+{count} nuevos!)")
            self.lbl_title.setStyleSheet("color: #10b981; font-size: 24px; font-weight: bold;")
            QTimer.singleShot(3000, self._reset_title)

    def _reset_title(self):
        self.lbl_title.setText("📥 Recepción de Equipos (Nube)")
        self.lbl_title.setStyleSheet("color: #e2e8f0; font-size: 24px; font-weight: bold;")
