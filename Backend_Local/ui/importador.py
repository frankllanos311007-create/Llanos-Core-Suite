import csv
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QMessageBox, QTextEdit, QFrame, QComboBox
)
from PyQt6.QtCore import Qt
import database

class ImportadorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setSpacing(20)

        # Title
        lbl_title = QLabel("📥 Importar Facturas / Datos")
        lbl_title.setStyleSheet("color: #e2e8f0; font-size: 24px; font-weight: bold;")
        lay.addWidget(lbl_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #1e293b; max-height: 1px;")
        lay.addWidget(sep)

        # Instructions
        instr = QLabel("Selecciona el tipo de datos que deseas importar y elige un archivo CSV.")
        instr.setStyleSheet("color: #94a3b8; font-size: 14px;")
        lay.addWidget(instr)

        # Controls
        row = QHBoxLayout()
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Notas de Entrega", "Ventas de Repuestos", "Ventas de Equipos", "Reportes de PC"])
        self.combo_type.setFixedWidth(250)
        self.combo_type.setFixedHeight(40)
        row.addWidget(self.combo_type)

        btn_select = QPushButton("📁 Seleccionar Archivo CSV")
        btn_select.setFixedHeight(40)
        btn_select.setFixedWidth(250)
        btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_select.clicked.connect(self._select_file)
        row.addWidget(btn_select)
        row.addStretch()
        lay.addLayout(row)

        # Log
        lbl_log = QLabel("Registro de Importación:")
        lbl_log.setStyleSheet("color: #A0A0A0; font-size: 12px; font-weight: bold;")
        lay.addWidget(lbl_log)

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background: #0f172a; border: 1px solid #334155; border-radius: 8px; color: #cbd5e1; font-family: Consolas; font-size: 11px;")
        lay.addWidget(self.txt_log)

        lay.addStretch()

    def _log(self, msg: str):
        self.txt_log.append(f"[{database.datetime.now().strftime('%H:%M:%S')}] {msg}")

    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar CSV", "", "CSV Files (*.csv)")
        if not path:
            return

        import_type = self.combo_type.currentText()
        self._log(f"Iniciando importación de '{import_type}' desde {path}...")
        
        try:
            with open(path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                count = 0
                errors = 0
                
                for row in reader:
                    try:
                        if import_type == "Notas de Entrega":
                            database.save_nota(row)
                        elif import_type == "Ventas de Repuestos":
                            database.save_venta(row)
                        elif import_type == "Ventas de Equipos":
                            database.save_venta_equipo(row)
                        elif import_type == "Reportes de PC":
                            database.save_reporte(row)
                        count += 1
                    except Exception as e:
                        self._log(f"Error en fila {count + errors + 1}: {e}")
                        errors += 1
                
                self._log(f"Importación finalizada. Éxito: {count}, Errores: {errors}")
                QMessageBox.information(self, "Importación", f"Se importaron {count} registros con éxito.")
                
        except Exception as e:
            self._log(f"Error crítico al leer el archivo: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo leer el archivo: {e}")

    def show_form(self): pass
    def show_history(self): pass
