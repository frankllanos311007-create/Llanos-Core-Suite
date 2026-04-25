from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton, 
    QFrame, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from printing.printer import print_raw_text

class NotasLibresWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(16)

        # ── Title row
        title_row = QHBoxLayout()
        lbl = QLabel("📝  Notas Libres")
        lbl.setStyleSheet("color:#e2e8f0;font-size:19px;font-weight:bold;")
        title_row.addWidget(lbl)
        title_row.addStretch()
        
        btn_clear = QPushButton("🗑️ Limpiar")
        btn_clear.setFixedWidth(100)
        btn_clear.setFixedHeight(36)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.clicked.connect(self._clear_text)
        title_row.addWidget(btn_clear)
        layout.addLayout(title_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#1e293b;max-height:1px;")
        layout.addWidget(sep)

        # ── Editor Card
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("""
            QFrame#card {
                background-color: #222222;
                border-radius: 10px;
                border: 1px solid #2A2A2A;
            }
        """)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(20, 20, 20, 20)
        card_lay.setSpacing(12)

        lbl_instr = QLabel("Escribe aquí el contenido de la nota:")
        lbl_instr.setStyleSheet("color: #A0A0A0; font-size: 12px; font-weight: bold;")
        card_lay.addWidget(lbl_instr)

        self.txt_content = QTextEdit()
        self.txt_content.setPlaceholderText("Escribe lo que sea aquí...")
        self.txt_content.setFont(QFont("Segoe UI Variable", 12))
        self.txt_content.setStyleSheet("""
            QTextEdit {
                background-color: #1C1C1C;
                border: 1px solid #323232;
                border-radius: 6px;
                padding: 12px;
                color: #FFFFFF;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border: 1px solid #10B981;
            }
        """)
        card_lay.addWidget(self.txt_content)
        
        layout.addWidget(card, 1)

        # ── Action buttons
        actions_lay = QHBoxLayout()
        
        self.btn_print = QPushButton("🖨️  Imprimir Nota")
        self.btn_print.setObjectName("btn_primary")
        self.btn_print.setFixedHeight(50)
        self.btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_print.setStyleSheet("""
            QPushButton#btn_primary {
                background-color: #10B981;
                border: 1px solid #059669;
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton#btn_primary:hover {
                background-color: #34D399;
            }
            QPushButton#btn_primary:pressed {
                background-color: #059669;
            }
        """)
        self.btn_print.clicked.connect(self._print_note)
        actions_lay.addWidget(self.btn_print)
        
        layout.addLayout(actions_lay)

    def _clear_text(self):
        if not self.txt_content.toPlainText().strip():
            return
            
        reply = QMessageBox.question(
            self, "Limpiar nota",
            "¿Estás seguro de que quieres borrar todo el texto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.txt_content.clear()

    def _print_note(self):
        text = self.txt_content.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Nota vacía", "No hay nada escrito para imprimir.")
            return

        try:
            # Enviar directamente a la impresora térmica
            # Se puede agregar un encabezado simple
            header = "--- NOTA LIBRE ---\n\n"
            footer = "\n\n------------------\n"
            print_raw_text(header + text + footer)
            QMessageBox.information(self, "Impresión Exitosa", "La nota ha sido enviada a la impresora.")
        except Exception as e:
            QMessageBox.critical(self, "Error de Impresión", f"No se pudo imprimir:\n{str(e)}")

    def show_form(self):
        """Requerido por el sistema de navegación de MainWindow"""
        pass

    def show_history(self):
        """Requerido por el sistema de navegación de MainWindow"""
        pass
