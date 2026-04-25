# ─── Application stylesheet Windows 11 ───────────────────────────────────────

APP_STYLE = """
/* ══ WINDOWS 11 SUN VALLEY DARK MATTE ══════════════════════════════════════ */
QMainWindow { background-color: #202020; }
QWidget {
    background-color: transparent;
    color: #FFFFFF;
    font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
    font-size: 13px;
}
QLabel { color: #E5E5E5; }

/* ══ INPUTS & COMBOBOX ═════════════════════════════════════════════════════ */
QLineEdit, QTextEdit, QComboBox {
    background-color: #1C1C1C;
    border: 1px solid #323232;
    border-bottom: 2px solid #555555;
    border-radius: 6px;
    padding: 8px 12px;
    color: #FFFFFF;
    selection-background-color: #10B981;
    selection-color: #FFFFFF;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #323232;
    border-bottom: 2px solid #10B981;
    background-color: #242424;
}
QLineEdit[readOnly="true"] {
    background-color: #1A1A1A;
    color: #10B981;
    font-weight: bold;
    border: 1px solid #2B2B2B;
    border-bottom: 1px solid #2B2B2B;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox::down-arrow { image: none; }
QComboBox QAbstractItemView {
    background-color: #2B2B2B;
    border: 1px solid #454545;
    border-radius: 6px;
    selection-background-color: #383838;
}

/* ══ TABLE WIDGET (WIN 11 LISTS) ═══════════════════════════════════════════ */
QTableWidget {
    background-color: #202020;
    alternate-background-color: #242424;
    border: 1px solid #323232;
    border-radius: 8px;
    gridline-color: #323232;
    color: #FFFFFF;
    outline: none;
}
QTableWidget::item {
    padding: 4px 10px;
    color: #FFFFFF;
    border: none;
}
QTableWidget::item:selected {
    background-color: #10B981;
    color: #FFFFFF;
}
QTableWidget::item:hover {
    background-color: #282828;
}
QTableWidget QLineEdit {
    background-color: #2D2D2D;
    border: 1px solid #10B981;
    color: #FFFFFF;
    padding: 2px;
}
QTableWidget QLineEdit:focus {
    background-color: #2D2D2D;
    border: 1px solid #10B981;
}

/* ── Encabezados de Tabla ── */
QHeaderView { background-color: #202020; border: none; }
QHeaderView::section {
    background-color: #2D2D2D;
    color: #A0A0A0;
    padding: 10px 14px;
    border: none;
    border-right: 1px solid #3F3F3F;
    border-bottom: 1px solid #3F3F3F;
    font-weight: bold;
    font-size: 11px;
}
QHeaderView::section:hover {
    color: #FFFFFF;
    background-color: #383838;
}

/* ══ SCROLLBARS WIN 11 REPLICA ═════════════════════════════════════════════ */
QScrollBar:vertical {
    background: transparent; width: 12px; margin: 0;
}
QScrollBar::handle:vertical { background: #555555; min-height: 20px; border-radius: 6px; margin: 3px; }
QScrollBar::handle:vertical:hover { background: #888888; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: transparent; height: 12px; margin: 0;
}
QScrollBar::handle:horizontal { background: #555555; min-width: 20px; border-radius: 6px; margin: 3px; }
QScrollBar::handle:horizontal:hover { background: #888888; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ══ GROUPBOX / CARDS ══════════════════════════════════════════════════════ */
QGroupBox {
    border: 1px solid #323232;
    border-radius: 8px;
    margin-top: 14px;
    padding: 20px 14px 14px;
    background-color: #282828;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #10B981;
    font-weight: bold;
    font-size: 12px;
    background-color: transparent;
}

QFrame#card {
    background-color: #222222;
    border-radius: 10px;
    border: 1px solid #2A2A2A;
}
QLabel#card_title {
    color: #10B981;
    font-weight: bold;
    font-size: 14px;
}

/* ══ BUTTONS WIN11 ═════════════════════════════════════════════════════════ */
QPushButton {
    background-color: #333333;
    color: #FFFFFF;
    border: 1px solid #454545;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
}
QPushButton:hover { background-color: #444444; border-color: #555555; }
QPushButton:pressed { background-color: #222222; border-color: #333333; }

QPushButton#btn_primary { background-color: #10B981; border: 1px solid #059669; color: #FFFFFF; }
QPushButton#btn_primary:hover { background-color: #34D399; border-color: #10B981; }
QPushButton#btn_primary:pressed { background-color: #059669; border-color: #047857; }

QPushButton#btn_success { background-color: #0F8554; border: 1px solid #0B5C3A; color: #FFFFFF; }
QPushButton#btn_success:hover { background-color: #14A468; border-color: #0F8554; }
QPushButton#btn_success:pressed { background-color: #0B5C3A; border-color: #08422A; }

QPushButton#btn_danger { background-color: #C42B1C; border: 1px solid #991D11; color: #FFFFFF; }
QPushButton#btn_danger:hover { background-color: #E23D2D; border-color: #C42B1C; }
QPushButton#btn_danger:pressed { background-color: #991D11; border-color: #72140A; }

QPushButton#btn_info { background-color: #0067C0; border: 1px solid #004D8F; color: #FFFFFF; }
QPushButton#btn_info:hover { background-color: #0078D4; border-color: #0067C0; }
QPushButton#btn_info:pressed { background-color: #004D8F; border-color: #003766; }

/* ══ STATUS BAR ════════════════════════════════════════════════════════════ */
QStatusBar {
    background-color: #202020;
    color: #A0A0A0;
    border-top: 1px solid #323232;
    font-size: 11px;
}
"""

SIDEBAR_STYLE = """
QWidget#sidebar {
    background-color: #202020;
    border-right: 1px solid #323232;
}
"""

NAV_BTN_STYLE = """
QPushButton#nav_btn {
    background-color: transparent;
    color: #CCCCCC;
    text-align: left;
    padding: 12px 22px;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 6px;
    margin: 2px 8px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton#nav_btn:hover {
    background-color: #2D2D2D;
    color: #FFFFFF;
}
"""

NAV_BTN_ACTIVE_STYLE = """
QPushButton#nav_btn_active {
    background-color: #2D2D2D;
    color: #10B981;
    text-align: left;
    padding: 12px 22px;
    border: none;
    border-left: 3px solid #10B981;
    border-radius: 6px;
    margin: 2px 8px;
    font-weight: bold;
    font-size: 13px;
}
"""
