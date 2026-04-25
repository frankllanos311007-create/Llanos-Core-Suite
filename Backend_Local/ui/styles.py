# ─── Carbon & Slate Modern SaaS Style ───────────────────────────────────────

APP_STYLE = """
/* ══ CARBON & SLATE DESIGN SYSTEM ══════════════════════════════════════════ */
QMainWindow { 
    background-color: #0B0E14; 
}

QWidget {
    background-color: transparent;
    color: #F0F6FC;
    font-family: 'Inter', 'Segoe UI Variable', 'Segoe UI', sans-serif;
    font-size: 13px;
}

QLabel { 
    color: #8B949E; 
}

/* ══ INPUTS & COMBOBOX (Modern SaaS Style) ══════════════════════════════════ */
QLineEdit, QTextEdit, QComboBox {
    background-color: #0D1117;
    border: 1px solid #30363D;
    border-radius: 6px;
    padding: 10px 14px;
    color: #F0F6FC;
    selection-background-color: #2F81F7;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #58A6FF;
    background-color: #161B22;
}

/* ══ COMBOBOX DROPDOWN (Fix for visibility) ═════════════════════════════════ */
QComboBox QAbstractItemView {
    background-color: #0D1117;
    color: #F0F6FC;
    border: 1px solid #30363D;
    selection-background-color: #161B22;
    selection-color: #58A6FF;
    outline: none;
}

QLineEdit[readOnly="true"] {
    background-color: #010409;
    color: #58A6FF;
    font-weight: 600;
    border: 1px solid #21262D;
}

/* ══ TABLE WIDGET (Minimalist List) ═════════════════════════════════════════ */
QTableWidget {
    background-color: #0D1117;
    alternate-background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 8px;
    gridline-color: #21262D;
    color: #F0F6FC;
    outline: none;
}

QTableWidget::item {
    padding: 12px;
    border-bottom: 1px solid #21262D;
}

QTableWidget::item:selected {
    background-color: #161B22;
    color: #58A6FF;
    border-left: 2px solid #58A6FF;
}

QTableWidget::item:hover {
    background-color: #161B22;
}

QHeaderView { 
    background-color: #161B22; 
    border: none; 
}

QHeaderView::section {
    background-color: #161B22;
    color: #8B949E;
    padding: 12px;
    border: none;
    border-bottom: 1px solid #30363D;
    font-weight: bold;
    font-size: 11px;
    text-transform: uppercase;
}

/* ══ SCROLLBARS (Slim & Subtle) ═════════════════════════════════════════════ */
QScrollBar:vertical {
    background: transparent; width: 8px; margin: 0;
}
QScrollBar::handle:vertical { 
    background: #30363D; min-height: 20px; border-radius: 4px; 
}
QScrollBar::handle:vertical:hover { 
    background: #484F58; 
}

QScrollBar:horizontal {
    background: transparent; height: 8px; margin: 0;
}
QScrollBar::handle:horizontal { 
    background: #30363D; min-width: 20px; border-radius: 4px; 
}

/* ══ CARDS / FRAMES ═════════════════════════════════════════════════════════ */
QFrame#card {
    background-color: #161B22;
    border-radius: 10px;
    border: 1px solid #30363D;
}

QLabel#card_title {
    color: #F0F6FC;
    font-weight: bold;
    font-size: 15px;
    margin-bottom: 4px;
}

/* ══ BUTTONS (Vercel/Linear Inspired) ═══════════════════════════════════════ */
QPushButton {
    background-color: #21262D;
    color: #C9D1D9;
    border: 1px solid #363B42;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover { 
    background-color: #30363D; 
    border-color: #8B949E;
    color: #F0F6FC;
}

QPushButton:pressed { 
    background-color: #0D1117; 
}

/* Primary - Blue */
QPushButton#btn_primary { 
    background-color: #238636; 
    border: 1px solid #2ea043; 
    color: #FFFFFF; 
}
QPushButton#btn_primary:hover { 
    background-color: #2ea043; 
}

/* Success - Green */
QPushButton#btn_success { 
    background-color: #238636; 
    border: 1px solid #2ea043; 
    color: #FFFFFF; 
}

/* Info - Cyan/Blue */
QPushButton#btn_info { 
    background-color: #21262D; 
    border: 1px solid #30363D; 
    color: #58A6FF; 
}
QPushButton#btn_info:hover {
    border-color: #58A6FF;
}

/* Danger - Red */
QPushButton#btn_danger { 
    background-color: #DA3633; 
    border: 1px solid #F85149; 
    color: #FFFFFF; 
}

/* ══ STATUS BAR ════════════════════════════════════════════════════════════ */
QStatusBar {
    background-color: #0B0E14;
    color: #8B949E;
    border-top: 1px solid #30363D;
    font-size: 11px;
}
"""

SIDEBAR_STYLE = """
QWidget#sidebar {
    background-color: #0D1117;
    border: 1px solid #30363D;
    border-radius: 16px;
}
"""

NAV_BTN_STYLE = """
QPushButton#nav_btn {
    background-color: transparent;
    color: #8B949E;
    text-align: left;
    padding: 12px 18px;
    border: none;
    border-radius: 10px;
    margin: 4px 12px;
    font-weight: 500;
    font-size: 13px;
}
QPushButton#nav_btn:hover {
    background-color: #161B22;
    color: #F0F6FC;
}
"""

NAV_BTN_ACTIVE_STYLE = """
QPushButton#nav_btn_active {
    background-color: #2F81F7;
    color: #FFFFFF;
    text-align: left;
    padding: 12px 18px;
    border: none;
    border-radius: 10px;
    margin: 4px 12px;
    font-weight: bold;
    font-size: 13px;
}
"""
