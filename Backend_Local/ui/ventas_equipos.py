import json
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QStackedWidget, QMessageBox, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QFont, QColor, QDesktopServices

import database
from printing.printer import build_venta_equipo_text, print_raw_text
from ui.selector_dialog import SelectorDialog

# Cambia esto por la URL donde subas el auto_registro.html
FORM_URL = "https://llanos-core-registro.vercel.app"


class VentasEquiposWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._saved_id = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300)
        self.search_timer.timeout.connect(self._refresh_history)
        self._setup_ui()
        self._new_venta_equipo()
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
        lbl = QLabel("💻  Nueva Venta de Equipo")
        lbl.setStyleSheet("color:#e2e8f0;font-size:19px;font-weight:bold;")
        title_row.addWidget(lbl)
        title_row.addStretch()
        btn_new = QPushButton("＋ Nueva")
        btn_new.setFixedHeight(36)
        btn_new.setFixedWidth(95)
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.setToolTip("Limpiar y crear nueva nota")
        btn_new.clicked.connect(self._new_venta_equipo)
        title_row.addWidget(btn_new)

        btn_import = QPushButton("📥 Importar")
        btn_import.setFixedHeight(36)
        btn_import.setFixedWidth(100)
        btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import.setToolTip("Cargar datos de una venta de equipo ya hecha")
        btn_import.clicked.connect(self._import_from_existing)
        title_row.addWidget(btn_import)
        
        lay.addLayout(title_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#1e293b;max-height:1px;")
        lay.addWidget(sep)

        # ── Document info
        grp_doc, lay_doc = self._create_card("Detalles")
        frm_doc = QFormLayout()
        lay_doc.addLayout(frm_doc)
        frm_doc.setSpacing(10)
        frm_doc.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.txt_numero = QLineEdit(); self.txt_numero.setReadOnly(True)
        self.txt_fecha  = QLineEdit(); self.txt_fecha.setReadOnly(True)
        self.txt_hora   = QLineEdit(); self.txt_hora.setReadOnly(True)
        frm_doc.addRow("N° Factura:", self.txt_numero)
        frm_doc.addRow("Fecha:",   self.txt_fecha)
        frm_doc.addRow("Hora:",    self.txt_hora)
        lay.addWidget(grp_doc)

        # ── Client info
        grp_cli, lay_cli = self._create_card("Cliente")
        frm_cli = QFormLayout()
        lay_cli.addLayout(frm_cli)
        frm_cli.setSpacing(10)
        frm_cli.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.txt_cliente  = QLineEdit(); self.txt_cliente.setPlaceholderText("Nombre completo...")
        self.txt_telefono = QLineEdit(); self.txt_telefono.setPlaceholderText("Ej: 0414-123-4567")
        self.txt_ci       = QLineEdit(); self.txt_ci.setPlaceholderText("Ej: V-12.345.678")
        self.txt_ci.editingFinished.connect(self._lookup_client)
        frm_cli.addRow("Nombre:",   self.txt_cliente)
        frm_cli.addRow("Teléfono:", self.txt_telefono)
        frm_cli.addRow("C.I.:",      self.txt_ci)
        
        btn_self = QPushButton("⚡ Cargar Registro")
        btn_self.setToolTip("Pegar código enviado por el cliente")
        btn_self.setStyleSheet("color: #60a5fa; font-weight: bold; border: 1px dashed #3b82f6; padding: 6px; border-radius: 6px;")
        btn_self.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_self.clicked.connect(self._import_from_self_code)
        
        btn_send_form = QPushButton("📲 Enviar Formulario")
        btn_send_form.setToolTip("Enviar link de registro al cliente por WhatsApp")
        btn_send_form.setStyleSheet("color: #34d399; font-weight: bold; border: 1px dashed #10b981; padding: 6px; border-radius: 6px;")
        btn_send_form.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_send_form.clicked.connect(self._send_registration_form)
        
        row_reg = QHBoxLayout()
        row_reg.addWidget(btn_self)
        row_reg.addWidget(btn_send_form)
        lay_cli.addLayout(row_reg)
        
        lay.addWidget(grp_cli)

        # ── Especificaciones del Equipo
        grp_specs, lay_specs = self._create_card("Especificaciones Técnicas del Equipo")
        lay_specs.setSpacing(12)
        
        row_sp1 = QHBoxLayout()
        self.txt_marca = QLineEdit(); self.txt_marca.setPlaceholderText("Marca (Ej. Dell, HP)")
        self.txt_modelo = QLineEdit(); self.txt_modelo.setPlaceholderText("Modelo (Ej. Optiplex 3020)")
        self.txt_serial = QLineEdit(); self.txt_serial.setPlaceholderText("Serial / Service Tag")
        row_sp1.addWidget(self.txt_marca); row_sp1.addWidget(self.txt_modelo); row_sp1.addWidget(self.txt_serial)
        
        row_sp2 = QHBoxLayout()
        self.txt_cpu = QLineEdit(); self.txt_cpu.setPlaceholderText("Procesador (Ej. Core i5 4ta Gen)")
        self.txt_ram = QLineEdit(); self.txt_ram.setPlaceholderText("Memoria RAM (Ej. 8GB DDR3)")
        self.txt_disco = QLineEdit(); self.txt_disco.setPlaceholderText("Almacenamiento (Ej. 256GB SSD)")
        row_sp2.addWidget(self.txt_cpu); row_sp2.addWidget(self.txt_ram); row_sp2.addWidget(self.txt_disco)

        row_sp3 = QHBoxLayout()
        self.txt_mother = QLineEdit(); self.txt_mother.setPlaceholderText("Placa Madre (Ej. ASUS H81M)")
        self.txt_fuente = QLineEdit(); self.txt_fuente.setPlaceholderText("Fuente de Poder (Ej. 500W Cert.)")
        self.txt_so = QLineEdit(); self.txt_so.setPlaceholderText("Sistema Operativo (Ej. Windows 11)")
        row_sp3.addWidget(self.txt_mother); row_sp3.addWidget(self.txt_fuente); row_sp3.addWidget(self.txt_so)

        row_sp4 = QHBoxLayout()
        self.txt_gpu = QLineEdit(); self.txt_gpu.setPlaceholderText("Memoria Gráfica (Opcional)")
        self.txt_dvd = QLineEdit(); self.txt_dvd.setPlaceholderText("Unidad DVD (Opcional)")
        row_sp4.addWidget(self.txt_gpu); row_sp4.addWidget(self.txt_dvd)

        row_sp5 = QHBoxLayout()
        self.txt_teclado = QLineEdit(); self.txt_teclado.setPlaceholderText("Teclado (Opcional)")
        self.txt_mouse = QLineEdit(); self.txt_mouse.setPlaceholderText("Mouse (Opcional)")
        row_sp5.addWidget(self.txt_teclado); row_sp5.addWidget(self.txt_mouse)

        row_sp6 = QHBoxLayout()
        self.txt_cables = QLineEdit(); self.txt_cables.setPlaceholderText("Combo de Cables (Opcional)")
        self.txt_wifi = QLineEdit(); self.txt_wifi.setPlaceholderText("Antena Wifi (Opcional)")
        row_sp6.addWidget(self.txt_cables); row_sp6.addWidget(self.txt_wifi)
        
        lay_specs.addLayout(row_sp1); lay_specs.addLayout(row_sp2); lay_specs.addLayout(row_sp3)
        lay_specs.addLayout(row_sp4); lay_specs.addLayout(row_sp5); lay_specs.addLayout(row_sp6)
        lay.addWidget(grp_specs)

        # ── Precio Directo
        grp_price, lay_price = self._create_card("Precio de Venta")
        row_pr = QHBoxLayout()
        lbl_p = QLabel("PRECIO TOTAL DEL EQUIPO ($):")
        lbl_p.setStyleSheet("color:#A0A0A0; font-size:16px; font-weight:bold;")
        row_pr.addWidget(lbl_p)
        
        self.txt_total = QLineEdit()
        self.txt_total.setPlaceholderText("0.00")
        self.txt_total.setFixedWidth(150)
        self.txt_total.setFixedHeight(40)
        self.txt_total.setStyleSheet("color:#10B981; font-size:22px; font-weight:bold; background:#1e293b; border: 1px solid #334155; border-radius: 6px; padding: 0 10px;")
        self.txt_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        row_pr.addWidget(self.txt_total)
        row_pr.addStretch()
        lay_price.addLayout(row_pr)
        lay.addWidget(grp_price)

        # ── Observaciones
        grp_obs, lay_obs = self._create_card("Garantía / Observaciones")
        self.txt_obs = QTextEdit()
        self.txt_obs.setPlaceholderText("Especifica tiempo de garantía y condiciones...")
        self.txt_obs.setFixedHeight(80)
        lay_obs.addWidget(self.txt_obs)
        lay.addWidget(grp_obs)

        # ── Action buttons
        grp_act, lay_act = self._create_card("")
        lay_act.setSpacing(10)
        row1 = QHBoxLayout()
        self.btn_save = QPushButton("💾  Guardar"); self.btn_save.setObjectName("btn_success"); self.btn_save.setFixedHeight(44)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_save.clicked.connect(self._save_venta_equipo)
        row1.addWidget(self.btn_save)
        self.btn_preview = QPushButton("👁  Ver Ticket"); self.btn_preview.setObjectName("btn_info"); self.btn_preview.setFixedHeight(44)
        self.btn_preview.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_preview.clicked.connect(self._preview_thermal)
        row1.addWidget(self.btn_preview)
        self.btn_export = QPushButton("📄  Exportar"); self.btn_export.setObjectName("btn_info"); self.btn_export.setFixedHeight(44)
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_export.clicked.connect(self._export_pdf)
        row1.addWidget(self.btn_export)
        self.btn_whatsapp = QPushButton("📲  WhatsApp")
        self.btn_whatsapp.setObjectName("btn_success")
        self.btn_whatsapp.setFixedHeight(44)
        self.btn_whatsapp.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_whatsapp.clicked.connect(self._send_whatsapp)
        row1.addWidget(self.btn_whatsapp)
        
        lay_act.addLayout(row1)
        row2 = QHBoxLayout()
        self.btn_print = QPushButton("🖨️  Imprimir"); self.btn_print.setObjectName("btn_primary"); self.btn_print.setFixedHeight(46)
        self.btn_print.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_print.clicked.connect(self._print_thermal)
        row2.addWidget(self.btn_print)
        lay_act.addLayout(row2)
        lay.addWidget(grp_act)
        lay.addStretch()

        return scroll

    def _build_history(self) -> QWidget:
        container = QWidget(); container.setStyleSheet("background-color: transparent;")
        lay = QVBoxLayout(container); lay.setContentsMargins(22, 22, 22, 22); lay.setSpacing(12)
        hdr = QHBoxLayout()
        lbl = QLabel("📋  Historial de Equipos"); lbl.setStyleSheet("color:#e2e8f0;font-size:17px;font-weight:bold;")
        hdr.addWidget(lbl); hdr.addStretch()
        self.search_venta = QLineEdit(); self.search_venta.setPlaceholderText("🔍 Buscar…"); self.search_venta.setFixedWidth(200); self.search_venta.setFixedHeight(36)
        self.search_venta.textChanged.connect(self.search_timer.start)
        hdr.addWidget(self.search_venta); lay.addLayout(hdr)
        self.history_table = QTableWidget(); self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["N°", "Fecha", "Cliente", "Ver/Impr.", "Elim."])
        hh = self.history_table.horizontalHeader(); hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed); hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed); hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch); hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed); hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.history_table.setColumnWidth(0, 80); self.history_table.setColumnWidth(1, 92); self.history_table.setColumnWidth(3, 95); self.history_table.setColumnWidth(4, 66)
        self.history_table.verticalHeader().setVisible(False); self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers); self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        lay.addWidget(self.history_table)
        return container

    def _new_venta_equipo(self):
        self._saved_id = None
        now = datetime.now()
        self.txt_numero.setText(database.get_next_venta_equipo_number())
        self.txt_fecha.setText(now.strftime("%d/%m/%Y"))
        self.txt_hora.setText(now.strftime("%I:%M %p"))
        self.txt_cliente.clear(); self.txt_telefono.clear(); self.txt_ci.clear()
        self.txt_marca.clear(); self.txt_modelo.clear(); self.txt_serial.clear()
        self.txt_cpu.clear(); self.txt_ram.clear(); self.txt_disco.clear()
        self.txt_mother.clear(); self.txt_fuente.clear(); self.txt_so.clear()
        self.txt_gpu.clear(); self.txt_dvd.clear()
        self.txt_teclado.clear(); self.txt_mouse.clear()
        self.txt_cables.clear(); self.txt_wifi.clear()
        self.txt_total.setText("0.00"); self.txt_obs.clear()

    def _import_from_existing(self):
        dlg = SelectorDialog("Importar Venta de Equipo Existente", database.get_all_ventas_equipos, self)
        if dlg.exec():
            data = dlg.selected_data
            if data:
                self._load_data(data)

    def _load_data(self, data: dict):
        self.txt_cliente.setText(data.get('cliente', ''))
        self.txt_telefono.setText(data.get('telefono', ''))
        self.txt_ci.setText(data.get('ci', ''))
        self.txt_obs.setPlainText(data.get('observaciones', ''))
        
        self.txt_marca.setText(data.get('marca', ''))
        self.txt_modelo.setText(data.get('modelo', ''))
        self.txt_serial.setText(data.get('serial', ''))
        self.txt_cpu.setText(data.get('procesador', ''))
        self.txt_ram.setText(data.get('ram', ''))
        self.txt_disco.setText(data.get('almacenamiento', ''))
        self.txt_mother.setText(data.get('tarjeta_madre', ''))
        self.txt_fuente.setText(data.get('fuente_poder', ''))
        self.txt_so.setText(data.get('so', ''))
        self.txt_gpu.setText(data.get('grafica', ''))
        self.txt_dvd.setText(data.get('dvd', ''))
        self.txt_teclado.setText(data.get('teclado', ''))
        self.txt_mouse.setText(data.get('mouse', ''))
        self.txt_cables.setText(data.get('combo_cables', ''))
        self.txt_wifi.setText(data.get('antena_wifi', ''))
        
        self.txt_total.setText(f"{data.get('total', 0.0):.2f}")
        QMessageBox.information(self, "Datos Cargados", "Se han importado los datos del cliente y especificaciones.")

    def _import_from_self_code(self):
        from PyQt6.QtWidgets import QInputDialog
        code, ok = QInputDialog.getMultiLineText(self, "Cargar Registro", "Pega el código generado por el cliente aquí:")
        if not ok or not code: return
        try:
            import base64, json
            decoded = base64.b64decode(code).decode('utf-8')
            data = json.loads(decoded)
            self.txt_cliente.setText(data.get('n', ''))
            self.txt_telefono.setText(data.get('t', ''))
            self.txt_ci.setText(data.get('c', ''))
            self.txt_marca.setText(data.get('e', ''))
            self.txt_serial.setText(data.get('s', ''))
            self.txt_obs.setPlainText(f"REPORTE DEL CLIENTE: {data.get('f', '')}")
            QMessageBox.information(self, "Carga Exitosa", "Se han cargado los datos del cliente y su equipo.")
        except Exception:
            QMessageBox.critical(self, "Error", "Código inválido.")

    def _lookup_client(self):
        ci = self.txt_ci.text().strip()
        if not ci: return
        client = database.get_cliente_by_ci(ci)
        if client:
            self.txt_cliente.setText(client['nombre'])
            self.txt_telefono.setText(client['telefono'])

    def _collect_data(self) -> dict:
        total_str = self.txt_total.text().replace(',', '.')
        try: total = float(total_str) if total_str else 0.0
        except ValueError: total = 0.0
        return {
            'numero': self.txt_numero.text(), 'fecha': self.txt_fecha.text(), 'hora': self.txt_hora.text(),
            'cliente': self.txt_cliente.text().strip(), 'telefono': self.txt_telefono.text().strip(), 'ci': self.txt_ci.text().strip(),
            'marca': self.txt_marca.text().strip(), 'modelo': self.txt_modelo.text().strip(), 'serial': self.txt_serial.text().strip(),
            'procesador': self.txt_cpu.text().strip(), 'ram': self.txt_ram.text().strip(), 'almacenamiento': self.txt_disco.text().strip(),
            'tarjeta_madre': self.txt_mother.text().strip(), 'fuente_poder': self.txt_fuente.text().strip(), 'so': self.txt_so.text().strip(),
            'grafica': self.txt_gpu.text().strip(), 'dvd': self.txt_dvd.text().strip(),
            'teclado': self.txt_teclado.text().strip(), 'mouse': self.txt_mouse.text().strip(),
            'combo_cables': self.txt_cables.text().strip(), 'antena_wifi': self.txt_wifi.text().strip(),
            'items_json': '[]', 'total': total, 'observaciones': self.txt_obs.toPlainText().strip()
        }

    def _save_venta_equipo(self):
        data = self._collect_data()
        if not data['cliente']: QMessageBox.warning(self, "Requerido", "Falta cliente."); return
        if self._saved_id: return
        try:
            self._saved_id = database.save_venta_equipo(data)
            self.btn_save.setText("✅  Guardada"); self.btn_save.setEnabled(False); self._refresh_history()
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def _preview_thermal(self):
        data = self._collect_data()
        if not data['cliente']: return
        self._show_text_preview(build_venta_equipo_text(data), f"Vista Previa — {data['numero']}")

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
        path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", f"{data['numero']}_equipo.pdf", "PDF (*.pdf)")
        if path:
            text = build_venta_equipo_text(data)
            doc = QTextDocument(); doc.setHtml(f'<pre style="font-family: Consolas; font-size: 10pt;">{text}</pre>')
            printer = QPrinter(QPrinter.PrinterMode.HighResolution); printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat); printer.setOutputFileName(path)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4)); printer.setPageMargins(QMarginsF(15, 15, 15, 15), QPageLayout.Unit.Millimeter)
            doc.print(printer); QMessageBox.information(self, "PDF", "Exportado.")

    def _print_thermal(self):
        data = self._collect_data()
        if not data['cliente']: return
        if not self._saved_id: self._save_venta_equipo()
        try: print_raw_text(build_venta_equipo_text(data)); QMessageBox.information(self, "Impresión", "Ticket enviado.")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def _refresh_history(self):
        query = self.search_venta.text() if hasattr(self, 'search_venta') else ''
        ventas = database.get_all_ventas_equipos(query)
        self.history_table.setRowCount(len(ventas))
        for row, nota in enumerate(ventas):
            n = QTableWidgetItem(nota['numero']); n.setForeground(QColor("#10B981")); n.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold)); self.history_table.setItem(row, 0, n)
            f = QTableWidgetItem(nota['fecha']); f.setForeground(QColor("#cbd5e1")); self.history_table.setItem(row, 1, f)
            self.history_table.setItem(row, 2, QTableWidgetItem(nota['cliente']))
            btn_ver = QPushButton("👁  Ver"); btn_ver.setStyleSheet("QPushButton{background:#2563eb;color:white;border-radius:6px;padding:5px 10px;font-size:11px;font-weight:600;} QPushButton:hover{background:#3b82f6;}")
            btn_ver.clicked.connect(lambda _, n=nota: self._show_text_preview(build_venta_equipo_text(n), f"Venta {n['numero']}"))
            self.history_table.setCellWidget(row, 3, self._wrap(btn_ver))
            btn_el = QPushButton("🗑"); btn_el.setStyleSheet("QPushButton{background:#dc2626;color:white;border-radius:6px;padding:5px 8px;font-size:13px;} QPushButton:hover{background:#ef4444;}")
            btn_el.clicked.connect(lambda _, nid=nota['id'], num=nota['numero']: self._delete(nid, num))
            self.history_table.setCellWidget(row, 4, self._wrap(btn_el)); self.history_table.setRowHeight(row, 44)

    @staticmethod
    def _wrap(btn: QPushButton) -> QWidget:
        w = QWidget(); w.setStyleSheet("background:transparent;"); h = QHBoxLayout(w); h.setContentsMargins(5, 4, 5, 4); h.addWidget(btn); return w
    def _delete(self, nota_id: int, numero: str):
        if QMessageBox.question(self, "Confirmar", f"¿Eliminar {numero}?") == QMessageBox.StandardButton.Yes:
            database.delete_venta_equipo(nota_id); self._refresh_history()
            if self._saved_id == nota_id: self._new_venta_equipo()

    def _send_whatsapp(self):
        data = self._collect_data()
        phone = data.get('telefono', '').strip()
        if not phone:
            QMessageBox.warning(self, "Falta Teléfono", "Por favor ingresa el número del cliente.")
            return
        
        # Clean phone number
        clean_phone = "".join(filter(str.isdigit, phone))
        if len(clean_phone) == 10 and clean_phone.startswith('4'): 
            clean_phone = "58" + clean_phone
        elif len(clean_phone) == 11 and clean_phone.startswith('0'):
            clean_phone = "58" + clean_phone[1:]
        
        # Format message
        msg = (
            f"Hola *{data['cliente']}*, le saluda *Llanos Core*. 👋\n\n"
            f"Le informamos que su equipo (Factura *{data['numero']}*) ya está listo para ser retirado.\n"
            f"Modelo: *{data['marca']} {data['modelo']}*.\n"
            f"Total: *${data['total']:.2f}*.\n\n"
            f"¡Gracias por su compra!"
        )
        
        import urllib.parse
        encoded_msg = urllib.parse.quote(msg)
        url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_msg}"
        QDesktopServices.openUrl(QUrl(url))

    def _send_registration_form(self):
        from PyQt6.QtWidgets import QInputDialog
        phone = self.txt_telefono.text().strip()
        if not phone:
            phone, ok = QInputDialog.getText(self, "WhatsApp", "Número del cliente:")
            if not ok or not phone: return
        
        clean_phone = "".join(filter(str.isdigit, phone))
        if len(clean_phone) == 10 and clean_phone.startswith('4'): clean_phone = "58" + clean_phone
        elif len(clean_phone) == 11 and clean_phone.startswith('0'): clean_phone = "58" + clean_phone[1:]
        
        msg = (
            f"Hola, le saluda *Llanos Core*. 👋\n\n"
            f"Para agilizar su recepción, por favor llene sus datos y los de su equipo en este link:\n"
            f"🔗 {FORM_URL}\n\n"
            f"Al finalizar, envíenos el código que genera el sistema. ¡Gracias!"
        )
        import urllib.parse
        url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={urllib.parse.quote(msg)}"
        QDesktopServices.openUrl(QUrl(url))
