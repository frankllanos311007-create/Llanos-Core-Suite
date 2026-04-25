from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QStatusBar, QFrame,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QIcon

from ui.notas_entrega import NotasEntregaWidget
from ui.reportes_pc import ReportesPCWidget
from ui.ventas_repuestos import VentasRepuestosWidget
from ui.ventas_equipos import VentasEquiposWidget
from ui.tasas import TasasWidget
from ui.notas_libres import NotasLibresWidget
from ui.clientes import ClientesWidget
from ui.recepcion import RecepcionWidget
from ui.styles import SIDEBAR_STYLE, NAV_BTN_STYLE, NAV_BTN_ACTIVE_STYLE
import database


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Llanos Core — Gestión SaaS")
        self.setMinimumSize(1100, 750)
        self.resize(1300, 850)
        
        # Icono del sistema
        self.setWindowIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))

        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── SIDEBAR CONTAINER (Para efecto flotante)
        self.sidebar_container = QWidget()
        self.sidebar_container.setFixedWidth(0) # Iniciar CERRADA al 100%
        self.sidebar_lay = QVBoxLayout(self.sidebar_container)
        self.sidebar_lay.setContentsMargins(0, 0, 0, 0) # Sin márgenes al estar cerrada
        
        self.sidebar = self._build_sidebar()
        self.sidebar_lay.addWidget(self.sidebar)
        
        root.addWidget(self.sidebar_container)

        # Right panel (topbar + content)
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)

        right_lay.addWidget(self._build_topbar())

        self.widget_notas = NotasEntregaWidget()
        self.widget_reportes = ReportesPCWidget()
        self.widget_ventas = VentasRepuestosWidget()
        self.widget_equipos = VentasEquiposWidget()
        self.widget_tasas = TasasWidget()
        self.widget_libres = NotasLibresWidget()
        self.widget_clientes = ClientesWidget()
        self.widget_recepcion = RecepcionWidget()
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.widget_notas)     # index 0
        self.stack.addWidget(self.widget_reportes)  # index 1
        self.stack.addWidget(self.widget_ventas)    # index 2
        self.stack.addWidget(self.widget_equipos)   # index 3
        self.stack.addWidget(self.widget_tasas)     # index 4
        self.stack.addWidget(self.widget_libres)    # index 5
        self.stack.addWidget(self.widget_clientes)  # index 6
        self.stack.addWidget(self.widget_recepcion) # index 7
        right_lay.addWidget(self.stack, 1)

        root.addWidget(right, 1)

        # Status bar
        sb = QStatusBar()
        sb.showMessage("⚡ Llanos Core  •  Enterprise SaaS Edition  •  Ready")
        self.setStatusBar(sb)

        self._navigate(0) # Iniciar en formulario de notas
        self.showMaximized()

    def closeEvent(self, event):
        """Asegura que el proceso se cierre completamente."""
        import sys
        sys.exit(0)

    # ── TOP BAR ───────────────────────────────────────────────────────────────

    def _build_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(65) # Un poco más alto para elegancia
        bar.setStyleSheet(
            "QWidget{"
            "background-color: transparent;"
            "border-bottom: 1px solid #21262D;}"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(25, 0, 30, 0)
        lay.setSpacing(16)

        self.btn_toggle = QPushButton("\uE700") # Icono oficial de Windows 11 (Burger)
        self.btn_toggle.setFixedSize(42, 42)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setStyleSheet(
            "QPushButton { background: #161B22; border: 1px solid #30363D; color: #F0F6FC; font-family: 'Segoe MDL2 Assets'; font-size: 16px; border-radius: 10px; }"
            "QPushButton:hover { background: #21262D; border-color: #58A6FF; color: #58A6FF; }"
        )
        self.btn_toggle.clicked.connect(self.toggle_sidebar)
        lay.addWidget(self.btn_toggle)

        self.topbar_title = QLabel("📦  Notas de Entrega")
        self.topbar_title.setStyleSheet(
            "color:#F0F6FC;font-size:18px;font-weight:600;letter-spacing:-0.5px;"
        )
        lay.addWidget(self.topbar_title)
        lay.addStretch()

        return bar

    # ── SIDEBAR ───────────────────────────────────────────────────────────────

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(SIDEBAR_STYLE)

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(0, 10, 0, 10)
        lay.setSpacing(0)

        # ── Logo block
        self.logo_block = QWidget()
        self.logo_block.setFixedHeight(100)
        lb = QVBoxLayout(self.logo_block)
        lb.setContentsMargins(25, 20, 25, 20)
        lb.setSpacing(2)

        self.lbl_logo = QLabel("⚡ LLANOS CORE")
        self.lbl_logo.setStyleSheet(
            "color: #58A6FF; font-size: 18px; font-weight: bold;"
            "letter-spacing: 1px; background: transparent; border: none;"
        )
        lb.addWidget(self.lbl_logo)

        self.lbl_sub = QLabel("Premium Document System")
        self.lbl_sub.setStyleSheet(
            "color:#484F58;font-size:10px;font-weight:bold;letter-spacing:0.5px;"
        )
        lb.addWidget(self.lbl_sub)
        lay.addWidget(self.logo_block)

        # ── Section label
        self.sec_lbl1 = QLabel("MÓDULOS")
        self.sec_lbl1.setStyleSheet(
            "color: #484F58; font-size: 10px; font-weight: bold; letter-spacing: 2px; padding: 15px 25px 8px;"
        )
        lay.addWidget(self.sec_lbl1)

        # ── Navigation buttons
        nav_items = [
            ("📦  Nota de Entrega", 0, 0, "📦  Nueva Nota de Entrega"),
            ("🖥️  Diagnósticos de PC", 1, 0, "🖥️  Nuevo Diagnóstico"),
            ("🛒  Ventas de Repuestos", 2, 0, "🛒  Nueva Venta de Repuestos"),
            ("💻  Venta de Equipos", 3, 0, "💻  Nueva Venta de Equipo"),
            ("📝  Notas Libres", 5, 0, "📝  Notas Libres"),
            ("👥  Clientes", 6, 0, "👥  Gestión de Clientes"),
            ("📥  Recepción Cloud", 7, 0, "📥  Recepción Cloud"),
        ]
        
        hist_items = [
            ("📋  Historial Notas",    0, 1, "📋  Historial de Notas"),
            ("📋  Historial Diagnósticos", 1, 1, "📋  Historial de Diagnósticos"),
            ("📋  Historial Ventas", 2, 1, "📋  Historial de Ventas"),
            ("📋  Historial Equipos", 3, 1, "📋  Historial de Equipos"),
        ]
        
        self._nav_btns: list[QPushButton] = []
        
        def _build_btn(label, mod_idx, sub_view, title):
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(45)
            btn.clicked.connect(lambda _, m=mod_idx, s=sub_view, t=title, i=len(self._nav_btns): self._navigate(i, m, s, t))
            lay.addWidget(btn)
            self._nav_btns.append(btn)

        for btn_data in nav_items:
            _build_btn(*btn_data)
            
        self.sec_lbl2 = QLabel("HISTORIALES")
        self.sec_lbl2.setStyleSheet(
            "color: #484F58; font-size: 10px; font-weight: bold; letter-spacing: 2px; padding: 20px 25px 8px;"
        )
        lay.addWidget(self.sec_lbl2)

        for btn_data in hist_items:
            _build_btn(*btn_data)

        lay.addStretch()

        self.ver = QLabel("Llanos Core v2.2")
        self.ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ver.setStyleSheet("color: #484F58; font-size: 11px; padding: 20px;")
        lay.addWidget(self.ver)

        return sidebar

    def toggle_sidebar(self):
        width = self.sidebar_container.width()
        new_width = 0 if width > 0 else 270 
        
        # Ajustar márgenes durante la animación
        if new_width == 270:
            self.sidebar_lay.setContentsMargins(15, 15, 0, 15)
        else:
            # Usar un timer para quitar márgenes DESPUÉS de que cierre
            QTimer.singleShot(300, lambda: self.sidebar_lay.setContentsMargins(0,0,0,0))

        self.anim = QPropertyAnimation(self.sidebar_container, b"minimumWidth")
        self.anim.setDuration(300)
        self.anim.setStartValue(width)
        self.anim.setEndValue(new_width)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        self.anim2 = QPropertyAnimation(self.sidebar_container, b"maximumWidth")
        self.anim2.setDuration(300)
        self.anim2.setStartValue(width)
        self.anim2.setEndValue(new_width)
        self.anim2.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        self.anim.start()
        self.anim2.start()

        # Al abrir (new_width > 0), nos aseguramos de que todo el contenido esté visible y completo
        if new_width > 0:
            self.lbl_logo.setText("⚡ LLANOS CORE")
            self.lbl_logo.setStyleSheet("color: #58A6FF; font-size: 18px; font-weight: bold; letter-spacing: 1px;")
            self.lbl_sub.show()
            self.sec_lbl1.show()
            self.sec_lbl2.show()
            self.ver.show()
            for btn in self._nav_btns:
                if hasattr(btn, 'full_text'): btn.setText(btn.full_text)
                btn.setToolTip("")

    def _navigate(self, btn_index: int, module_idx: int = 0, sub_view: int = 0, title: str = "📦  Nota de Entrega"):
        self.stack.setCurrentIndex(module_idx)
        active_widget = self.stack.currentWidget()
        
        if hasattr(active_widget, "show_form"):
            if sub_view == 0: active_widget.show_form()
            else: active_widget.show_history()

        self.topbar_title.setText(title)
        
        for i, btn in enumerate(self._nav_btns):
            if i == btn_index: btn.setObjectName("nav_btn_active")
            else: btn.setObjectName("nav_btn")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
