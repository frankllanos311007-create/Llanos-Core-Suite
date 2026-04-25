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
from printing.printer import build_nota_text, print_raw_text
from ui.selector_dialog import SelectorDialog

# Cambia esto por la URL donde subas el auto_registro.html
FORM_URL = "https://tu-usuario.github.io/tu-repo/auto_registro.html"


class NotasEntregaWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._saved_id = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300)
        self.search_timer.timeout.connect(self._refresh_history)
        self._setup_ui()
        self._new_nota()
        self._refresh_history()
        self.items_table.installEventFilter(self)

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
        self.items_table.installEventFilter(self)
        self.main_stack.setCurrentIndex(1)

    def _build_form(self) -> QScrollArea:
        container = QWidget()
        container.setObjectName("formContainer")
        container.setStyleSheet("QWidget#formContainer { background-color: transparent; }")

        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

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
        lbl = QLabel("📦  Nueva Nota de Entrega")
        lbl.setStyleSheet("color:#e2e8f0;font-size:19px;font-weight:bold;")
        title_row.addWidget(lbl)
        title_row.addStretch()
        btn_new = QPushButton("＋ Nueva")
        btn_new.setFixedHeight(36)
        btn_new.setFixedWidth(95)
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.setToolTip("Limpiar y crear nueva nota")
        btn_new.clicked.connect(self._new_nota)
        title_row.addWidget(btn_new)

        btn_import = QPushButton("📥 Importar")
        btn_import.setFixedHeight(36)
        btn_import.setFixedWidth(100)
        btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import.setToolTip("Cargar datos de una nota ya hecha")
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
        frm_doc.addRow("N° Nota:", self.txt_numero)
        frm_doc.addRow("Fecha:",   self.txt_fecha)
        frm_doc.addRow("Hora:",    self.txt_hora)
        lay.addWidget(grp_doc)

        # ── Client info
        grp_cli, lay_cli = self._create_card("Datos del Cliente")
        row_cli = QHBoxLayout()
        self.txt_cliente  = QLineEdit(); self.txt_cliente.setPlaceholderText("Nombre completo...")
        self.txt_telefono = QLineEdit(); self.txt_telefono.setPlaceholderText("Teléfono (Opcional)")
        self.txt_ci       = QLineEdit(); self.txt_ci.setPlaceholderText("Ej: V-12.345.678")
        self.txt_ci.editingFinished.connect(self._lookup_client)
        row_cli.addWidget(self.txt_cliente)
        row_cli.addWidget(self.txt_telefono)
        row_cli.addWidget(self.txt_ci)
        lay_cli.addLayout(row_cli)
        
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

        # ── Items
        grp_items, lay_items = self._create_card("Artículos")
        lay_items.setSpacing(10)

        self.txt_quick_add = QLineEdit()
        self.txt_quick_add.setPlaceholderText("🛒 Escribe el artículo aquí y presiona Enter...")
        self.txt_quick_add.setFixedHeight(38)
        self.txt_quick_add.returnPressed.connect(self._quick_add_item)
        lay_items.addWidget(self.txt_quick_add)

        toolbar = QHBoxLayout()
        btn_add = QPushButton("＋  Agregar")
        btn_add.setObjectName("btn_success")
        btn_add.setFixedHeight(34)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._add_item_row)
        toolbar.addWidget(btn_add)

        btn_del = QPushButton("✕  Eliminar")
        btn_del.setObjectName("btn_danger")
        btn_del.setFixedHeight(34)
        btn_del.setFixedWidth(100)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(self._remove_item_row)
        toolbar.addWidget(btn_del)
        lay_items.addLayout(toolbar)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["#", "Descripción", "Precio ($)", "Cant.", "Subtotal ($)"])
        hh = self.items_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.items_table.setColumnWidth(0, 42)
        self.items_table.setColumnWidth(2, 90)
        self.items_table.setColumnWidth(3, 72)
        self.items_table.setColumnWidth(4, 100)
        self.items_table.setFixedHeight(190)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.itemChanged.connect(self._on_item_changed)
        lay_items.addWidget(self.items_table)

        # ── Total row
        total_row = QHBoxLayout()
        total_row.addStretch()
        lbl_t_text = QLabel("TOTAL:")
        lbl_t_text.setStyleSheet("color:#A0A0A0; font-size:16px; font-weight:bold;")
        total_row.addWidget(lbl_t_text)
        
        self.lbl_total = QLabel("$0.00")
        self.lbl_total.setStyleSheet("color:#10B981; font-size:24px; font-weight:bold; margin-left: 10px;")
        total_row.addWidget(self.lbl_total)
        lay_items.addLayout(total_row)
        
        lay.addWidget(grp_items)

        # ── Observaciones
        grp_obs, lay_obs = self._create_card("Diagnóstico")
        self.txt_obs = QTextEdit()
        self.txt_obs.setPlaceholderText("Notas adicionales, condiciones...")
        self.txt_obs.setFixedHeight(95)
        lay_obs.addWidget(self.txt_obs)
        lay.addWidget(grp_obs)

        # ── Action buttons
        grp_act, lay_act = self._create_card("")
        lay_act.setSpacing(10)

        row1 = QHBoxLayout()
        self.btn_save = QPushButton("💾  Guardar")
        self.btn_save.setObjectName("btn_success")
        self.btn_save.setFixedHeight(44)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self._save_nota)
        row1.addWidget(self.btn_save)

        self.btn_preview = QPushButton("👁  Ver Ticket")
        self.btn_preview.setObjectName("btn_info")
        self.btn_preview.setFixedHeight(44)
        self.btn_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_preview.clicked.connect(self._preview_thermal)
        row1.addWidget(self.btn_preview)
        
        self.btn_export = QPushButton("📄  Exportar")
        self.btn_export.setObjectName("btn_info")
        self.btn_export.setFixedHeight(44)
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.clicked.connect(self._export_pdf)
        row1.addWidget(self.btn_export)
        
        self.btn_whatsapp = QPushButton("📲  WhatsApp")
        self.btn_whatsapp.setObjectName("btn_success")
        self.btn_whatsapp.setFixedHeight(44)
        self.btn_whatsapp.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_whatsapp.clicked.connect(self._send_whatsapp)
        row1.addWidget(self.btn_whatsapp)
        
        lay_act.addLayout(row1)

        row2 = QHBoxLayout()
        self.btn_print = QPushButton("🖨️  Imprimir")
        self.btn_print.setObjectName("btn_primary")
        self.btn_print.setFixedHeight(46)
        self.btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_print.clicked.connect(self._print_thermal)
        row2.addWidget(self.btn_print)
        lay_act.addLayout(row2)

        lay.addWidget(grp_act)
        lay.addStretch()

        return scroll

    def _build_history(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")

        lay = QVBoxLayout(container)
        lay.setContentsMargins(22, 22, 22, 22)
        lay.setSpacing(12)

        hdr = QHBoxLayout()
        lbl = QLabel("📋  Historial de Notas")
        lbl.setStyleSheet("color:#e2e8f0;font-size:17px;font-weight:bold;")
        hdr.addWidget(lbl)
        hdr.addStretch()

        self.search_nota = QLineEdit()
        self.search_nota.setPlaceholderText("🔍 Buscar…")
        self.search_nota.setFixedWidth(200)
        self.search_nota.setFixedHeight(36)
        self.search_nota.textChanged.connect(self.search_timer.start)
        hdr.addWidget(self.search_nota)
        lay.addLayout(hdr)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["N°", "Fecha", "Cliente", "Ver/Impr.", "Elim."])
        hh = self.history_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.history_table.setColumnWidth(0, 80)
        self.history_table.setColumnWidth(1, 92)
        self.history_table.setColumnWidth(3, 95)
        self.history_table.setColumnWidth(4, 66)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        lay.addWidget(self.history_table)

        return container

    # ── FORM LOGIC ────────────────────────────────────────────────────────────

    def _new_nota(self):
        self._saved_id = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300)
        self.search_timer.timeout.connect(self._refresh_history)
        now = datetime.now()
        self.txt_numero.setText(database.get_next_nota_number())
        self.txt_fecha.setText(now.strftime("%d/%m/%Y"))
        self.txt_hora.setText(now.strftime("%I:%M %p"))
        self.txt_cliente.clear()
        self.txt_telefono.clear()
        self.txt_ci.clear()
        self.txt_obs.clear()
        self.txt_quick_add.clear()
        self.items_table.setRowCount(0)

    def _import_from_existing(self):
        dlg = SelectorDialog("Importar Nota Existente", database.get_all_notas, self)
        if dlg.exec():
            data = dlg.selected_data
            if data:
                self._load_data(data)

    def _load_data(self, data: dict):
        # We keep the current Number, Date, and Time
        # But load the rest
        self.txt_cliente.setText(data.get('cliente', ''))
        self.txt_telefono.setText(data.get('telefono', ''))
        self.txt_ci.setText(data.get('ci', ''))
        self.txt_obs.setPlainText(data.get('observaciones', ''))
        
        items = json.loads(data.get('items_json', '[]'))
        self.items_table.setRowCount(0)
        for item in items:
            row = self.items_table.rowCount()
            self._add_item_row()
            self.items_table.item(row, 1).setText(item.get('descripcion', ''))
            self.items_table.item(row, 2).setText(f"{item.get('precio', 0.0):.2f}")
            self.items_table.item(row, 3).setText(str(item.get('cantidad', 1)))
        
        self._calculate_total()
        QMessageBox.information(self, "Datos Cargados", "Se han importado los datos del cliente y artículos.")

    def _quick_add_item(self):
        desc = self.txt_quick_add.text().strip()
        if not desc:
            return
        row = self.items_table.rowCount()
        self._add_item_row()
        self.items_table.item(row, 1).setText(desc)
        self.txt_quick_add.clear()
        self.items_table.setCurrentCell(row, 2)
        self.items_table.editItem(self.items_table.item(row, 2))

    def _add_item_row(self):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)

        num_item = QTableWidgetItem(str(row + 1))
        num_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        num_item.setForeground(QColor("#10B981"))
        self.items_table.setItem(row, 0, num_item)

        self.items_table.setItem(row, 1, QTableWidgetItem(""))

        price_item = QTableWidgetItem("0.00")
        price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.items_table.setItem(row, 2, price_item)

        qty_item = QTableWidgetItem("1")
        qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.items_table.setItem(row, 3, qty_item)

        sub_item = QTableWidgetItem("0.00")
        sub_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        sub_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.items_table.setItem(row, 4, sub_item)

        self.items_table.setRowHeight(row, 38)
        self.items_table.blockSignals(False)
        self._calculate_total()

    def _remove_item_row(self):
        selected = self.items_table.selectionModel().selectedRows()
        self.items_table.blockSignals(True)
        if selected:
            for idx in reversed([r.row() for r in selected]):
                self.items_table.removeRow(idx)
        elif self.items_table.rowCount() > 1:
            self.items_table.removeRow(self.items_table.rowCount() - 1)

        # Re-number
        for i in range(self.items_table.rowCount()):
            item = QTableWidgetItem(str(i + 1))
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor("#10B981"))
            self.items_table.setItem(i, 0, item)
        self.items_table.blockSignals(False)
        self._calculate_total()
        
    def _on_item_changed(self, item):
        if item.column() in (2, 3):  # Si cambia precio o cantidad
            self._calculate_total()

    def _calculate_total(self):
        total = 0.0
        self.items_table.blockSignals(True)
        for row in range(self.items_table.rowCount()):
            p_item = self.items_table.item(row, 2)
            q_item = self.items_table.item(row, 3)
            sub_item = self.items_table.item(row, 4)
            
            try:
                p = float(p_item.text().strip().replace(',', '.')) if p_item and p_item.text().strip() else 0.0
                q = int(q_item.text().strip()) if q_item and q_item.text().strip() else 0
            except ValueError:
                p = 0.0; q = 0
                
            sub = p * q
            total += sub
            if sub_item: sub_item.setText(f"{sub:.2f}")
                
        self.items_table.blockSignals(False)
        self.lbl_total.setText(f"${total:.2f}")
        return total

    def _collect_data(self) -> dict:
        items = []
        for row in range(self.items_table.rowCount()):
            d = self.items_table.item(row, 1); p = self.items_table.item(row, 2); q = self.items_table.item(row, 3)
            desc = d.text().strip() if d else ''
            precio = p.text().strip().replace(',', '.') if p else '0.0'
            qty  = q.text().strip() if q else '1'
            if desc:
                items.append({'descripcion': desc, 'precio': float(precio) if precio else 0.0, 'cantidad': qty or '1'})

        return {
            'numero':       self.txt_numero.text(),
            'fecha':        self.txt_fecha.text(),
            'hora':         self.txt_hora.text(),
            'cliente':      self.txt_cliente.text().strip(),
            'telefono':     self.txt_telefono.text().strip(),
            'ci':           self.txt_ci.text().strip(),
            'items_json':   json.dumps(items, ensure_ascii=False),
            'total':        self._calculate_total(),
            'observaciones': self.txt_obs.toPlainText().strip(),
        }

    def _validate(self, data: dict) -> bool:
        if not data['cliente']:
            QMessageBox.warning(self, "Campo requerido", "El nombre del cliente es obligatorio.")
            self.txt_cliente.setFocus()
            return False
        if not json.loads(data['items_json']):
            QMessageBox.warning(self, "Sin repuestos", "Agrega al menos un repuesto a la nota.")
            return False
        return True

    # ── ACTIONS ───────────────────────────────────────────────────────────────

    def _save_nota(self):
        data = self._collect_data()
        if not self._validate(data):
            return
        if self._saved_id:
            QMessageBox.information(self, "Ya guardada",
                                    f"La nota {data['numero']} ya está guardada.")
            return
        try:
            self._saved_id = database.save_nota(data)
            self.btn_save.setText("✅  Guardada")
            self.btn_save.setEnabled(False)
            self._refresh_history()
            self.items_table.installEventFilter(self)
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", str(e))

    def _preview_thermal(self):
        data = self._collect_data()
        if not data['cliente']:
            QMessageBox.warning(self, "Datos incompletos", "Completa al menos el nombre del cliente.")
            return
        text_content = build_nota_text(data)
        self._show_text_preview(text_content, f"Vista Previa — {data['numero']}")

    def _show_text_preview(self, text: str, title: str):
        from PyQt6.QtWidgets import QDialog, QTextEdit
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.resize(420, 600)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(0, 0, 0, 0)
        t = QTextEdit()
        t.setReadOnly(True)
        t.setStyleSheet("background: white; color: black;")
        font = QFont("Consolas", 10)
        t.setFont(font)
        t.setPlainText(text)
        lay.addWidget(t)
        dlg.exec()



    def _export_pdf(self):
        data = self._collect_data()
        if not data['cliente']:
            QMessageBox.warning(self, "Datos incompletos", "Completa al menos el nombre del cliente.")
            return
            
        from PyQt6.QtWidgets import QFileDialog
        from PyQt6.QtPrintSupport import QPrinter
        from PyQt6.QtGui import QTextDocument, QPageSize, QPageLayout
        from PyQt6.QtCore import QSizeF, QMarginsF
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar como PDF", f"{data['numero']}_termica.pdf", "PDF (*.pdf)"
        )
        if path:
            text = build_nota_text(data)
            html = f'<pre style="font-family: Consolas, monospace; font-size: 10pt; margin: 0; padding: 0;">{text}</pre>'
            doc = QTextDocument()
            doc.setHtml(html)
            
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(path)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            printer.setPageMargins(QMarginsF(15, 15, 15, 15), QPageLayout.Unit.Millimeter)
            
            doc.print(printer)
            QMessageBox.information(self, "PDF Exportado", f"Documento guardado en:\n{path}")

    def _print_thermal(self):
        data = self._collect_data()
        if not self._validate(data):
            return
        if not self._saved_id:
            reply = QMessageBox.question(
                self, "Guardar antes de imprimir",
                "La nota aún no fue guardada. ¿Guardar ahora?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._save_nota()
                
        try:
            print_raw_text(build_nota_text(data))
            QMessageBox.information(self, "Impresión Exitosa", "Ticket enviado a la impresora correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error de Impresión", str(e))



    def eventFilter(self, source, event):
        from PyQt6.QtCore import QEvent
        if source == self.items_table and event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                curr = self.items_table.currentIndex()
                row, col = curr.row(), curr.column()
                
                if col == 2: # Price -> Move to Qty
                    self.items_table.setCurrentCell(row, 3)
                    self.items_table.editItem(self.items_table.item(row, 3))
                    return True
                elif col == 3: # Qty -> Back to Quick Add
                    self.txt_quick_add.setFocus()
                    return True
            
            if event.key() == Qt.Key.Key_Delete:
                self._remove_item_row()
                return True
                
        return super().eventFilter(source, event)

    # ── HISTORY ───────────────────────────────────────────────────────────────

    def _refresh_history(self):
        query = self.search_nota.text() if hasattr(self, 'search_nota') else ''
        notas = database.get_all_notas(query)
        self.history_table.setRowCount(len(notas))

        for row, nota in enumerate(notas):
            n = QTableWidgetItem(nota['numero'])
            n.setForeground(QColor("#10B981"))
            n.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.history_table.setItem(row, 0, n)

            f = QTableWidgetItem(nota['fecha'])
            f.setForeground(QColor("#cbd5e1")) # Gris azulado claro brillante
            self.history_table.setItem(row, 1, f)

            self.history_table.setItem(row, 2, QTableWidgetItem(nota['cliente']))

            btn_ver = QPushButton("👁  Ver")
            btn_ver.setStyleSheet(
                "QPushButton{background:#2563eb;color:white;border-radius:6px;"
                "padding:5px 10px;font-size:11px;font-weight:600;}"
                "QPushButton:hover{background:#3b82f6;}"
            )
            btn_ver.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_ver.clicked.connect(
                lambda _, n=nota: self._show_text_preview(
                    build_nota_text(n),
                    f"Nota {n['numero']} — {n['cliente']}"
                )
            )
            self.history_table.setCellWidget(row, 3, self._wrap(btn_ver))

            btn_el = QPushButton("🗑")
            btn_el.setStyleSheet(
                "QPushButton{background:#dc2626;color:white;border-radius:6px;"
                "padding:5px 8px;font-size:13px;}"
                "QPushButton:hover{background:#ef4444;}"
            )
            btn_el.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_el.clicked.connect(
                lambda _, nid=nota['id'], num=nota['numero']: self._delete(nid, num)
            )
            self.history_table.setCellWidget(row, 4, self._wrap(btn_el))

            self.history_table.setRowHeight(row, 44)

    @staticmethod
    def _wrap(btn: QPushButton) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w)
        h.setContentsMargins(5, 4, 5, 4)
        h.addWidget(btn)
        return w

    def _delete(self, nota_id: int, numero: str):
        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Eliminar la nota {numero}?\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_nota(nota_id)
            self._refresh_history()
            if self._saved_id == nota_id:
                self._new_nota()

    def _lookup_client(self):
        import database
        ci = self.txt_ci.text().strip()
        if not ci: return
        client = database.get_cliente_by_ci(ci)
        if client:
            self.txt_cliente.setText(client['nombre'])
            self.txt_telefono.setText(client['telefono'])

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
            f"Le informamos que sus artículos (Nota *{data['numero']}*) ya están listos para ser retirados.\n"
            f"Total: *${data['total']:.2f}*.\n\n"
            f"¡Gracias por su preferencia!"
        )
        
        import urllib.parse
        encoded_msg = urllib.parse.quote(msg)
        url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_msg}"
        QDesktopServices.openUrl(QUrl(url))

    def _import_from_self_code(self):
        from PyQt6.QtWidgets import QInputDialog
        code, ok = QInputDialog.getMultiLineText(self, "Cargar Registro", "Pega el código generado por el cliente aquí:")
        if not ok or not code: return
        try:
            import base64
            decoded = base64.b64decode(code).decode('utf-8')
            data = json.loads(decoded)
            self.txt_cliente.setText(data.get('n', ''))
            self.txt_telefono.setText(data.get('t', ''))
            self.txt_ci.setText(data.get('c', ''))
            self.txt_obs.setPlainText(f"REPORTE DEL CLIENTE: {data.get('f', '')}")
            QMessageBox.information(self, "Carga Exitosa", "Se han cargado los datos del cliente.")
        except Exception:
            QMessageBox.critical(self, "Error", "Código inválido.")

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
            f"Para agilizar su recepción, por favor llene sus datos en este link:\n"
            f"🔗 {FORM_URL}\n\n"
            f"Al finalizar, envíenos el código que genera el sistema. ¡Gracias!"
        )
        import urllib.parse
        url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={urllib.parse.quote(msg)}"
        QDesktopServices.openUrl(QUrl(url))
