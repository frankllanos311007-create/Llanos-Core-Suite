from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import database

class TasasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_rate()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setSpacing(20)

        # Title
        lbl_title = QLabel("💵 Configuración de Tasas de Cambio")
        lbl_title.setStyleSheet("color: #e2e8f0; font-size: 24px; font-weight: bold;")
        lay.addWidget(lbl_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #1e293b; max-height: 1px;")
        lay.addWidget(sep)

        # Card
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("""
            QFrame#card {
                background-color: #1e293b;
                border-radius: 12px;
                border: 1px solid #334155;
            }
        """)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(30, 30, 30, 30)
        card_lay.setSpacing(20)

        grid = QGridLayout()
        grid.setSpacing(15)

        lbl_desc = QLabel("Tasa de cambio actual (USD -> BS):")
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 16px;")
        grid.addWidget(lbl_desc, 0, 0)

        self.txt_rate = QLineEdit()
        self.txt_rate.setPlaceholderText("Ej: 45.50")
        self.txt_rate.setFixedWidth(200)
        self.txt_rate.setFixedHeight(45)
        self.txt_rate.setStyleSheet("""
            QLineEdit {
                background: #0f172a;
                border: 2px solid #334155;
                border-radius: 8px;
                color: #10B981;
                font-size: 20px;
                font-weight: bold;
                padding-left: 10px;
            }
            QLineEdit:focus {
                border-color: #10B981;
            }
        """)
        grid.addWidget(self.txt_rate, 1, 0)

        btn_save = QPushButton("💾 Actualizar Tasa")
        btn_save.setFixedHeight(45)
        btn_save.setFixedWidth(200)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background: #10B981;
                color: #000;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #34d399;
            }
        """)
        btn_save.clicked.connect(self._save_rate)
        grid.addWidget(btn_save, 1, 1)

        card_lay.addLayout(grid)
        
        info = QLabel("💡 Esta tasa se aplicará automáticamente a todos los tickets y notas de entrega para mostrar el equivalente en Bolívares.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #64748b; font-size: 13px; font-style: italic;")
        card_lay.addWidget(info)

        lay.addWidget(card)
        lay.addStretch()

    def _load_rate(self):
        rate = database.get_exchange_rate()
        self.txt_rate.setText(f"{rate:.2f}")

    def _save_rate(self):
        try:
            val = float(self.txt_rate.text().replace(',', '.'))
            if val <= 0: raise ValueError
            database.set_exchange_rate(val)
            QMessageBox.information(self, "Tasa Actualizada", f"La nueva tasa es: Bs {val:.2f}")
            
            # Update topbar in main window if possible
            main_win = self.window()
            if hasattr(main_win, "rate_badge"):
                main_win.rate_badge.setText(f"BCV: Bs {val:.2f}")
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingresa un número válido.")
