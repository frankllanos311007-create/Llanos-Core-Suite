from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QStatusBar, QFrame,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

from ui.notas_entrega import NotasEntregaWidget
from ui.reportes_pc import ReportesPCWidget
from ui.ventas_repuestos import VentasRepuestosWidget
from ui.ventas_equipos import VentasEquiposWidget
from ui.tasas import TasasWidget
from ui.notas_libres import NotasLibresWidget
from ui.clientes import ClientesWidget
from ui.styles import SIDEBAR_STYLE, NAV_BTN_STYLE, NAV_BTN_ACTIVE_STYLE
import database


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Llanos Core — Gestión de Documentos")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        root.addWidget(self._build_sidebar())

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
        
        self.stack = QStackedWidget()
        self.stack.addWidget(self.widget_notas)     # index 0
        self.stack.addWidget(self.widget_reportes)  # index 1
        self.stack.addWidget(self.widget_ventas)    # index 2
        self.stack.addWidget(self.widget_equipos)   # index 3
        self.stack.addWidget(self.widget_tasas)     # index 4
        self.stack.addWidget(self.widget_libres)    # index 5
        self.stack.addWidget(self.widget_clientes)  # index 6
        right_lay.addWidget(self.stack, 1)

        root.addWidget(right, 1)

        # Status bar
        sb = QStatusBar()
        sb.showMessage("⚡ Llanos Core  •  Sistema de Gestión Premium  •  Listo")
        self.setStatusBar(sb)

        self._navigate(0) # Iniciar en formulario de notas

    # ── TOP BAR ───────────────────────────────────────────────────────────────

    def _build_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(56)
        bar.setStyleSheet(
            "QWidget{"
            "background-color: #202020;"
            "border-bottom: 1px solid #323232;}"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(18, 0, 22, 0)
        lay.setSpacing(16)

        self.btn_toggle = QPushButton("☰")
        self.btn_toggle.setFixedSize(36, 36)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: #A0A0A0; font-size: 20px; border-radius: 6px; padding: 0; }"
            "QPushButton:hover { background: #2D2D2D; color: #FFFFFF; }"
        )
        self.btn_toggle.clicked.connect(self.toggle_sidebar)
        lay.addWidget(self.btn_toggle)

        self.topbar_title = QLabel("📦  Notas de Entrega")
        self.topbar_title.setStyleSheet(
            "color:#F8FAFC;font-size:16px;font-weight:bold;"
            "letter-spacing:0.5px;background:transparent;border:none;"
        )
        lay.addStretch()

        lay.addStretch()

        hint = QLabel("👁 Vista Previa   │   💾 Guardar   │   🖨️ Imprimir   │   📄 PDF")
        hint.setStyleSheet(
            "color: #4A5568; font-size: 11px; background: transparent; border: none;"
        )
        lay.addWidget(hint)

        return bar

    # ── SIDEBAR ───────────────────────────────────────────────────────────────

    def _build_sidebar(self) -> QWidget:
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet(SIDEBAR_STYLE)

        lay = QVBoxLayout(self.sidebar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Logo block
        self.logo_block = QWidget()
        self.logo_block.setFixedHeight(85)
        self.logo_block.setStyleSheet(
            "QWidget{"
            "background-color: #202020;"
            "border-bottom: 1px solid #323232;}"
        )
        lb = QVBoxLayout(self.logo_block)
        lb.setContentsMargins(20, 16, 20, 16)
        lb.setSpacing(4)

        self.lbl_logo = QLabel("⚡ LLANOS CORE")
        self.lbl_logo.setStyleSheet(
            "color: #10B981; font-size: 18px; font-weight: bold;"
            "letter-spacing: 1px; background: transparent; border: none;"
        )
        lb.addWidget(self.lbl_logo)

        self.lbl_sub = QLabel("Gestión de Documentos")
        self.lbl_sub.setStyleSheet(
            "color:#A0A0A0;font-size:10px;letter-spacing:1px;"
            "background:transparent;border:none;font-weight:bold;"
        )
        lb.addWidget(self.lbl_sub)
        lay.addWidget(self.logo_block)

        # ── Section label
        self.sec_lbl1 = QLabel("MÓDULOS")
        self.sec_lbl1.setStyleSheet(
            "color: #A0A0A0; font-size: 10px; font-weight: bold; letter-spacing: 1.5px;"
            "padding: 16px 20px 8px; background: transparent; border: none;"
        )
        lay.addWidget(self.sec_lbl1)

        # ── Navigation buttons
        nav_items = [
            # label, module_idx, sub_view (0=form, 1=hist), title
            ("📦  Nota de Entrega", 0, 0, "📦  Nueva Nota de Entrega"),
            ("🖥️  Diagnósticos de PC", 1, 0, "🖥️  Nuevo Diagnóstico"),
            ("🛒  Ventas de Repuestos", 2, 0, "🛒  Nueva Venta de Repuestos"),
            ("💻  Venta de Equipos", 3, 0, "💻  Nueva Venta de Equipo"),
            ("📝  Notas Libres", 5, 0, "📝  Notas Libres"),
            ("👥  Clientes", 6, 0, "👥  Gestión de Clientes"),
        ]
        
        hist_items = [
            ("📋  Historial Notas",    0, 1, "📋  Historial de Notas"),
            ("📋  Historial Diagnósticos", 1, 1, "📋  Historial de Diagnósticos"),
            ("📋  Historial Ventas", 2, 1, "📋  Historial de Ventas"),
            ("📋  Historial Equipos", 3, 1, "📋  Historial de Equipos"),
        ]
        
        self._nav_btns: list[QPushButton] = []
        self._nav_funcs = []
        self._nav_titles: list[str] = []
        
        # Helper iterador
        def _build_btn(label, mod_idx, sub_view, title):
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Conectar
            btn.clicked.connect(lambda _, m=mod_idx, s=sub_view, t=title, i=len(self._nav_btns): self._navigate(i, m, s, t))
            lay.addWidget(btn)
            self._nav_btns.append(btn)

        for btn_data in nav_items:
            _build_btn(*btn_data)
            
        # Label separador Historial
        self.sec_lbl2 = QLabel("HISTORIALES")
        self.sec_lbl2.setStyleSheet(
            "color: #A0A0A0; font-size: 10px; font-weight: bold; letter-spacing: 1.5px;"
            "padding: 16px 20px 8px; background: transparent; border: none;"
        )
        lay.addWidget(self.sec_lbl2)

        for btn_data in hist_items:
            _build_btn(*btn_data)

        lay.addStretch()

        lay.addStretch()

        # ── Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("background: #323232; max-height: 1px; border: none;")
        lay.addWidget(div)

        # ── Version footer
        self.ver = QLabel("Llanos Core  v2.0")
        self.ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ver.setStyleSheet(
            "color: #A0A0A0; font-size: 11px; padding: 16px; background: transparent; border: none;"
        )
        lay.addWidget(self.ver)

        return self.sidebar

    def toggle_sidebar(self):
        width = self.sidebar.width()
        # Toggle between fully open (240px) and closed (68px)
        new_width = 68 if width > 100 else 240
        self.anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.anim.setDuration(300)
        self.anim.setStartValue(width)
        self.anim.setEndValue(new_width)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        self.anim2 = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.anim2.setDuration(300)
        self.anim2.setStartValue(width)
        self.anim2.setEndValue(new_width)
        self.anim2.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        self.anim.start()
        self.anim2.start()

        # Hide extra text when collapsed
        if new_width == 68:
            self.lbl_logo.setText("⚡")
            self.lbl_logo.setStyleSheet("color: #10B981; font-size: 24px; margin-left:-2px; font-weight: bold; background: transparent; border: none;")
            self.lbl_sub.hide()
            self.sec_lbl1.hide()
            self.sec_lbl2.hide()
            self.sec_lbl3.hide()
            self.ver.hide()
            
            # Cortar a solo emoji
            for btn in self._nav_btns:
                if not hasattr(btn, 'full_text'):
                    btn.full_text = btn.text()
                # Extrae el emoji (separando por el doble espacio)
                btn.setText(btn.full_text.split("  ")[0])
        else:
            self.lbl_logo.setText("⚡ LLANOS CORE")
            self.lbl_logo.setStyleSheet("color: #10B981; font-size: 18px; font-weight: bold; letter-spacing: 1px; background: transparent; border: none;")
            self.lbl_sub.show()
            self.sec_lbl1.show()
            self.sec_lbl2.show()
            self.sec_lbl3.show()
            self.ver.show()
            
            # Restaurar texto
            for btn in self._nav_btns:
                if hasattr(btn, 'full_text'):
                    btn.setText(btn.full_text)

    # ── NAVIGATION ────────────────────────────────────────────────────────────

    def _navigate(self, btn_index: int, module_idx: int = 0, sub_view: int = 0, title: str = "📦  Nota de Entrega"):
        # Cambiar widget principal en el stack general
        self.stack.setCurrentIndex(module_idx)
        
        # Obtener el widget activo
        if module_idx == 0:
            active_widget = self.widget_notas
        elif module_idx == 1:
            active_widget = self.widget_reportes
        elif module_idx == 2:
            active_widget = self.widget_ventas
        elif module_idx == 3:
            active_widget = self.widget_equipos
        elif module_idx == 5:
            active_widget = self.widget_libres
        elif module_idx == 6:
            active_widget = self.widget_clientes
        else:
            active_widget = self.widget_tasas
        
        # Configurar la subvista (0=Form, 1=History)
        if hasattr(active_widget, "show_form"):
            if sub_view == 0:
                active_widget.show_form()
            else:
                active_widget.show_history()

        self.topbar_title.setText(title)
        
        # Desactivar / activar los colores de los botones
        for i, btn in enumerate(self._nav_btns):
            if i == btn_index:
                btn.setObjectName("nav_btn_active")
            else:
                btn.setObjectName("nav_btn")
            
            # Forzar actualización de estilo
            btn.style().unpolish(btn)
            btn.style().polish(btn)
