from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QStackedWidget, QMessageBox, QScrollArea,
    QFrame, QComboBox,
)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QFont, QColor, QDesktopServices

import database
from printing.printer import build_reporte_text, print_raw_text
from ui.selector_dialog import SelectorDialog

# Cambia esto por la URL donde subas el auto_registro.html
FORM_URL = "https://llanos-core-registro.vercel.app"


class ReportesPCWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._saved_id = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300)
        self.search_timer.timeout.connect(self._refresh_history)
        self._setup_ui()
        self._new_reporte()
        self._refresh_history()

    # ── UI CONSTRUCTION ───────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.main_stack = QStackedWidget()
        self.form_widget = self._build_form()
        self.history_widget = self._build_history()

        self.main_stack.addWidget(self.form_widget)
        self.main_stack.addWidget(self.history_widget)

        layout.addWidget(self.main_stack)

    def show_form(self):
        self.main_stack.setCurrentIndex(0)

    def show_history(self):
        self._refresh_history()
        self.main_stack.setCurrentIndex(1)

    def _create_card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("card")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(20, 16, 20, 20)
        card_lay.setSpacing(12)
        if title:
            lbl_title = QLabel(title)
            lbl_title.setObjectName("card_title")
            card_lay.addWidget(lbl_title)
        return card, card_lay

    def _add_field(self, lay, label, widget):
        v_lay = QVBoxLayout()
        v_lay.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #8B949E; font-size: 11px; font-weight: bold; margin-left: 2px;")
        v_lay.addWidget(lbl)
        v_lay.addWidget(widget)
        lay.addLayout(v_lay)

    def _build_form(self) -> QScrollArea:
        container = QWidget()
        container.setObjectName("formContainer")
        container.setStyleSheet("QWidget#formContainer { background-color: transparent; }")

        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        lay = QVBoxLayout(container)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        # ── Title row
        title_row = QHBoxLayout()
        lbl = QLabel("🖥️  Nuevo Reporte de PC")
        lbl.setStyleSheet("color:#F0F6FC;font-size:19px;font-weight:bold;")
        title_row.addWidget(lbl)
        title_row.addStretch()
        btn_new = QPushButton("＋ Nuevo")
        btn_new.setFixedHeight(36); btn_new.setFixedWidth(95); btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.clicked.connect(self._new_reporte)
        title_row.addWidget(btn_new)

        btn_import = QPushButton("📥 Importar")
        btn_import.setFixedHeight(36); btn_import.setFixedWidth(100); btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import.clicked.connect(self._import_from_existing)
        title_row.addWidget(btn_import)
        lay.addLayout(title_row)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setStyleSheet("background:#30363D;max-height:1px;")
        lay.addWidget(sep)

        # ── Document info
        grp_doc, lay_doc = self._create_card("Detalles")
        frm_doc = QFormLayout(); lay_doc.addLayout(frm_doc); frm_doc.setSpacing(10); frm_doc.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.txt_numero = QLineEdit(); self.txt_numero.setReadOnly(True)
        self.txt_fecha  = QLineEdit(); self.txt_fecha.setReadOnly(True)
        self.txt_hora   = QLineEdit(); self.txt_hora.setReadOnly(True)
        frm_doc.addRow("N° Reporte:", self.txt_numero)
        frm_doc.addRow("Fecha:",      self.txt_fecha)
        frm_doc.addRow("Hora:",       self.txt_hora)
        lay.addWidget(grp_doc)

        # ── Client info
        grp_cli, lay_cli = self._create_card("Datos del Cliente")
        row_cli = QHBoxLayout(); row_cli.setSpacing(12)
        self.txt_cliente  = QLineEdit()
        self.txt_cliente.returnPressed.connect(self._lookup_client_by_name)
        self.txt_telefono = QLineEdit()
        self.txt_ci       = QLineEdit()
        self.txt_ci.editingFinished.connect(self._lookup_client)
        
        self._add_field(row_cli, "NOMBRE DEL CLIENTE", self.txt_cliente)
        self._add_field(row_cli, "TELÉFONO", self.txt_telefono)
        self._add_field(row_cli, "CÉDULA / RIF", self.txt_ci)
        lay_cli.addLayout(row_cli)
        lay.addWidget(grp_cli)

        # ── Equipment info
        grp_eq, lay_eq = self._create_card("Datos del Equipo")
        row_eq = QHBoxLayout(); row_eq.setSpacing(12)
        self.txt_marca  = QLineEdit()
        self.txt_modelo = QLineEdit()
        self.txt_serial = QLineEdit()
        
        self._add_field(row_eq, "MARCA", self.txt_marca)
        self._add_field(row_eq, "MODELO", self.txt_modelo)
        self._add_field(row_eq, "SERIAL / TAG", self.txt_serial)
        
        lay_eq.addLayout(row_eq)
        lay.addWidget(grp_eq)

        # ── Diagnóstico
        grp_diag, lay_diag = self._create_card("Diagnóstico")
        self.txt_diagnostico = QTextEdit()
        self.txt_diagnostico.setMinimumHeight(155)
        lay_diag.addWidget(self.txt_diagnostico)
        lay.addWidget(grp_diag)

        # ── Status & Cost
        grp_st, lay_st = self._create_card("Estado y Costo")
        row_st = QHBoxLayout(); row_st.setSpacing(12)
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["En Revisión", "Listo", "Entregado"])
        self.combo_estado.setFixedHeight(38)
        self.txt_costo = QLineEdit()
        
        self._add_field(row_st, "ESTADO ACTUAL", self.combo_estado)
        self._add_field(row_st, "COSTO ESTIMADO ($/Bs)", self.txt_costo)
        
        lay_st.addLayout(row_st)
        lay.addWidget(grp_st)

        # ── Action buttons
        grp_act, lay_act = self._create_card("")
        lay_act.setSpacing(10); row1 = QHBoxLayout()
        self.btn_save = QPushButton("💾  Guardar"); self.btn_save.setObjectName("btn_success"); self.btn_save.setFixedHeight(44); self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_save.clicked.connect(self._save_reporte)
        row1.addWidget(self.btn_save)
        self.btn_preview = QPushButton("👁  Ver Ticket"); self.btn_preview.setObjectName("btn_info"); self.btn_preview.setFixedHeight(44); self.btn_preview.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_preview.clicked.connect(self._preview_thermal)
        row1.addWidget(self.btn_preview)
        self.btn_export = QPushButton("📄  Exportar"); self.btn_export.setObjectName("btn_info"); self.btn_export.setFixedHeight(44); self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_export.clicked.connect(self._export_pdf)
        row1.addWidget(self.btn_export)
        self.btn_whatsapp = QPushButton("📲  WhatsApp"); self.btn_whatsapp.setObjectName("btn_success"); self.btn_whatsapp.setFixedHeight(44); self.btn_whatsapp.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_whatsapp.clicked.connect(self._send_whatsapp)
        row1.addWidget(self.btn_whatsapp); lay_act.addLayout(row1)
        row2 = QHBoxLayout()
        self.btn_print = QPushButton("🖨️  Imprimir"); self.btn_print.setObjectName("btn_primary"); self.btn_print.setFixedHeight(46); self.btn_print.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_print.clicked.connect(self._print_thermal)
        row2.addWidget(self.btn_print); lay_act.addLayout(row2)
        lay.addWidget(grp_act); lay.addStretch()
        return scroll

    def _build_history(self) -> QWidget:
        container = QWidget(); container.setStyleSheet("background-color: transparent;")
        lay = QVBoxLayout(container); lay.setContentsMargins(22, 22, 22, 22); lay.setSpacing(12)
        hdr = QHBoxLayout()
        lbl = QLabel("📋  Historial de Reportes"); lbl.setStyleSheet("color:#e2e8f0;font-size:17px;font-weight:bold;")
        hdr.addWidget(lbl); hdr.addStretch()
        self.search_rep = QLineEdit(); self.search_rep.setPlaceholderText("🔍 Buscar…"); self.search_rep.setFixedWidth(200); self.search_rep.setFixedHeight(36)
        self.search_rep.textChanged.connect(self.search_timer.start)
        hdr.addWidget(self.search_rep); lay.addLayout(hdr)
        self.history_table = QTableWidget(); self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["N°", "Fecha", "Cliente", "Estado", "Ver/Impr.", "Elim."])
        hh = self.history_table.horizontalHeader(); hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed); hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed); hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch); hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed); hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed); hh.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.history_table.setColumnWidth(0, 78); self.history_table.setColumnWidth(1, 88); self.history_table.setColumnWidth(3, 100); self.history_table.setColumnWidth(4, 95); self.history_table.setColumnWidth(5, 58)
        self.history_table.verticalHeader().setVisible(False); self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        lay.addWidget(self.history_table)
        return container

    # ── FORM LOGIC ────────────────────────────────────────────────────────────

    def _new_reporte(self):
        self._saved_id = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300)
        self.search_timer.timeout.connect(self._refresh_history)
        now = datetime.now()
        self.txt_numero.setText(database.get_next_reporte_number())
        self.txt_fecha.setText(now.strftime("%d/%m/%Y"))
        self.txt_hora.setText(now.strftime("%I:%M %p"))
        for w in (self.txt_cliente, self.txt_telefono, self.txt_ci,
                  self.txt_marca, self.txt_modelo, self.txt_serial,
                  self.txt_costo):
            w.clear()
        self.txt_diagnostico.clear()
        self.combo_estado.setCurrentIndex(0)

    def _import_from_existing(self):
        dlg = SelectorDialog("Importar Diagnóstico Existente", database.get_all_reportes, self)
        if dlg.exec():
            data = dlg.selected_data
            if data:
                self._load_data(data)

    def _load_data(self, data: dict):
        self.txt_cliente.setText(data.get('cliente', ''))
        self.txt_telefono.setText(data.get('telefono', ''))
        self.txt_ci.setText(data.get('ci', ''))
        self.txt_marca.setText(data.get('marca', ''))
        self.txt_modelo.setText(data.get('modelo', ''))
        self.txt_serial.setText(data.get('serial', ''))
        self.txt_diagnostico.setPlainText(data.get('diagnostico', ''))
        self.txt_costo.setText(data.get('costo', ''))
        index = self.combo_estado.findText(data.get('estado', ''), Qt.MatchFlag.MatchFixedString)
        if index >= 0: self.combo_estado.setCurrentIndex(index)
        QMessageBox.information(self, "Datos Cargados", "Se han importado los datos del cliente y diagnóstico.")
        self.btn_save.setText("💾  Guardar"); self.btn_save.setEnabled(True)

    def _lookup_client_by_name(self):
        nombre = self.txt_cliente.text().strip()
        if not nombre or len(nombre) < 3: return
        cloud = database.search_cloud_registration(nombre)
        if cloud:
            self.txt_cliente.setText(cloud['nombre'])
            self.txt_telefono.setText(cloud['telefono'])
            self.txt_ci.setText(cloud['ci'])
            self.txt_marca.setText(cloud.get('equipo', ''))
            self.txt_serial.setText(cloud.get('serial', ''))
            self.txt_diagnostico.setPlainText(f"FALLA REPORTADA POR CLIENTE: {cloud.get('falla', '')}")
            return
        client = database.get_cliente_by_name(nombre)
        if client:
            self.txt_ci.setText(client['ci'])
            self.txt_telefono.setText(client['telefono'])

    def _lookup_client(self):
        ci = self.txt_ci.text().strip()
        if not ci: return
        client = database.get_cliente_by_ci(ci)
        if client:
            self.txt_cliente.setText(client['nombre'])
            self.txt_telefono.setText(client['telefono'])

    def _collect_data(self) -> dict:
        return {
            'numero':      self.txt_numero.text(),
            'fecha':       self.txt_fecha.text(),
            'hora':        self.txt_hora.text(),
            'cliente':     self.txt_cliente.text().strip(),
            'telefono':    self.txt_telefono.text().strip(),
            'ci':          self.txt_ci.text().strip(),
            'marca':       self.txt_marca.text().strip(),
            'modelo':      self.txt_modelo.text().strip(),
            'serial':      self.txt_serial.text().strip(),
            'diagnostico': self.txt_diagnostico.toPlainText().strip(),
            'estado':      self.combo_estado.currentText(),
            'costo':       self.txt_costo.text().strip(),
        }

    def _validate(self, data: dict) -> bool:
        if not data['cliente']:
            QMessageBox.warning(self, "Campo requerido", "El nombre del cliente es obligatorio.")
            self.txt_cliente.setFocus(); return False
        return True

    def _save_reporte(self):
        data = self._collect_data()
        if not self._validate(data): return
        if self._saved_id: return
        try:
            self._saved_id = database.save_reporte(data)
            self.btn_save.setText("✅  Guardado"); self.btn_save.setEnabled(False); self._refresh_history()
        except Exception as e: QMessageBox.critical(self, "Error al guardar", str(e))

    def _preview_thermal(self):
        data = self._collect_data()
        if not data['cliente']: return
        self._show_text_preview(build_reporte_text(data), f"Vista Previa — {data['numero']}")

    def _show_text_preview(self, text: str, title: str):
        from PyQt6.QtWidgets import QDialog, QTextEdit
        dlg = QDialog(self); dlg.setWindowTitle(title); dlg.resize(420, 600)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(0, 0, 0, 0)
        t = QTextEdit(); t.setReadOnly(True); t.setStyleSheet("background: white; color: black;"); t.setFont(QFont("Consolas", 10)); t.setPlainText(text)
        lay.addWidget(t); dlg.exec()

    def _export_pdf(self):
        data = self._collect_data()
        if not data['cliente']: return
        from PyQt6.QtWidgets import QFileDialog; from PyQt6.QtPrintSupport import QPrinter; from PyQt6.QtGui import QTextDocument, QPageSize, QPageLayout; from PyQt6.QtCore import QSizeF, QMarginsF
        path, _ = QFileDialog.getSaveFileName(self, "Guardar como PDF", f"{data['numero']}_termica.pdf", "PDF (*.pdf)")
        if path:
            text = build_reporte_text(data)
            html = f'<pre style="font-family: Consolas, monospace; font-size: 7.5pt; margin: 0; padding: 0;">{text}</pre>'
            doc = QTextDocument(); doc.setHtml(html)
            printer = QPrinter(QPrinter.PrinterMode.HighResolution); printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat); printer.setOutputFileName(path)
            page_size = QPageSize(QSizeF(80, 200), QPageSize.Unit.Millimeter)
            printer.setPageSize(page_size); printer.setPageMargins(QMarginsF(3, 3, 3, 3), QPageLayout.Unit.Millimeter)
            doc.print(printer); QMessageBox.information(self, "PDF Exportado", f"Documento guardado en:\n{path}")

    def _print_thermal(self):
        data = self._collect_data()
        if not self._validate(data): return
        if not self._saved_id: self._save_reporte()
        try: print_raw_text(build_reporte_text(data)); QMessageBox.information(self, "Impresión Exitosa", "Ticket enviado.")
        except Exception as e: QMessageBox.critical(self, "Error de Impresión", str(e))

    def _send_whatsapp(self):
        data = self._collect_data()
        phone = data.get('telefono', '').strip()
        if not phone:
            QMessageBox.warning(self, "Falta Teléfono", "Por favor ingresa el número del cliente.")
            return
        clean_phone = "".join(filter(str.isdigit, phone))
        if len(clean_phone) == 10 and clean_phone.startswith('4'): clean_phone = "58" + clean_phone
        elif len(clean_phone) == 11 and clean_phone.startswith('0'): clean_phone = "58" + clean_phone[1:]
        msg = (f"Hola *{data['cliente']}*, le saluda *Llanos Core*. 👋\n\n"
               f"Le informamos que su equipo (Reporte *{data['numero']}*) ya se encuentra **{data['estado']}**.\n"
               f"Costo del servicio: *{data['costo']}*.\n\n¡Feliz día!")
        import urllib.parse
        encoded_msg = urllib.parse.quote(msg)
        url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_msg}"
        QDesktopServices.openUrl(QUrl(url))

    def _refresh_history(self):
        query = self.search_rep.text() if hasattr(self, 'search_rep') else ''
        reportes = database.get_all_reportes(query)
        self.history_table.setRowCount(len(reportes))
        estado_colors = {'En Revisión': '#fbbf24', 'Listo': '#34d399', 'Entregado': '#60a5fa'}
        for row, rep in enumerate(reportes):
            n = QTableWidgetItem(rep['numero']); n.setForeground(QColor("#10B981")); n.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold)); self.history_table.setItem(row, 0, n)
            f = QTableWidgetItem(rep['fecha']); f.setForeground(QColor("#cbd5e1")); self.history_table.setItem(row, 1, f)
            self.history_table.setItem(row, 2, QTableWidgetItem(rep['cliente']))
            estado = rep.get('estado', 'En Revisión')
            e = QTableWidgetItem(estado); e.setForeground(QColor(estado_colors.get(estado, '#64748b'))); e.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold)); self.history_table.setItem(row, 3, e)
            btn_ver = QPushButton("👁  Ver"); btn_ver.setStyleSheet("QPushButton{background:#2563eb;color:white;border-radius:6px;padding:5px 10px;font-size:11px;font-weight:600;} QPushButton:hover{background:#3b82f6;}")
            btn_ver.clicked.connect(lambda _, r=rep: self._show_text_preview(build_reporte_text(r), f"Reporte {r['numero']} — {r['cliente']}"))
            self.history_table.setCellWidget(row, 4, self._wrap(btn_ver))
            btn_el = QPushButton("🗑"); btn_el.setStyleSheet("QPushButton{background:#dc2626;color:white;border-radius:6px;padding:5px 8px;font-size:13px;} QPushButton:hover{background:#ef4444;}")
            btn_el.clicked.connect(lambda _, rid=rep['id'], num=rep['numero']: self._delete(rid, num))
            self.history_table.setCellWidget(row, 5, self._wrap(btn_el)); self.history_table.setRowHeight(row, 44)

    @staticmethod
    def _wrap(btn: QPushButton) -> QWidget:
        w = QWidget(); w.setStyleSheet("background:transparent;"); h = QHBoxLayout(w); h.setContentsMargins(5, 4, 5, 4); h.addWidget(btn); return w
    def _delete(self, rep_id: int, numero: str):
        if QMessageBox.question(self, "Confirmar", f"¿Eliminar el reporte {numero}?") == QMessageBox.StandardButton.Yes:
            database.delete_reporte(rep_id); self._refresh_history()
            if self._saved_id == rep_id: self._new_reporte()
