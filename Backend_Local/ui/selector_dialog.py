from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
import database

class SelectorDialog(QDialog):
    def __init__(self, title: str, fetch_func, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(650, 450)
        self.fetch_func = fetch_func
        self.selected_data = None
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300)
        self.search_timer.timeout.connect(self._refresh)
        
        self._setup_ui()
        self._refresh()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("🔍 Buscar:"))
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Número, cliente...")
        self.txt_search.textChanged.connect(self.search_timer.start)
        hdr.addWidget(self.txt_search)
        lay.addLayout(hdr)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["N°", "Fecha", "Cliente"])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 100)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._on_accept)
        lay.addWidget(self.table)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        
        btn_ok = QPushButton("Seleccionar y Cargar")
        btn_ok.setStyleSheet("background: #2563eb; color: white; font-weight: bold; padding: 6px 12px;")
        btn_ok.clicked.connect(self._on_accept)
        btns.addWidget(btn_ok)
        lay.addLayout(btns)

    def _refresh(self):
        query = self.txt_search.text()
        self.results = self.fetch_func(query)
        self.table.setRowCount(len(self.results))
        for row, data in enumerate(self.results):
            n = QTableWidgetItem(data.get('numero', ''))
            n.setForeground(QColor("#10B981"))
            n.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row, 0, n)
            self.table.setItem(row, 1, QTableWidgetItem(data.get('fecha', '')))
            self.table.setItem(row, 2, QTableWidgetItem(data.get('cliente', '')))

    def _on_accept(self):
        row = self.table.currentRow()
        if row >= 0:
            self.selected_data = self.results[row]
            self.accept()
        else:
            self.reject()
