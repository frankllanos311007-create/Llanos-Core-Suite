import json
import win32print
import database

# ─── THERMAL PRINTER SETTINGS ────────────────────────────────────────────────
# Standard 80mm thermal printers support 48 characters per line (Font A).
WIDTH = 48

def _center(text: str) -> str:
    if len(text) >= WIDTH:
        return text[:WIDTH]
    pad = (WIDTH - len(text)) // 2
    return (' ' * pad) + text + (' ' * (WIDTH - len(text) - pad))

def _left_right(left: str, right: str) -> str:
    left = str(left)
    right = str(right)
    if len(left) + len(right) >= WIDTH:
        return left[:WIDTH - len(right) - 1] + ' ' + right
    spaces = WIDTH - len(left) - len(right)
    return left + (' ' * spaces) + right

def _line() -> str:
    return '-' * WIDTH

def _thick_line() -> str:
    return '=' * WIDTH


# ─── RAW PRINT ENGINE ────────────────────────────────────────────────────────

def get_printer_name() -> str:
    """Finds the XP-80C printer or uses default."""
    try:
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        # 1. Prefer explicitly XP-80C
        for p in printers:
            name = p[2]
            if "XP-80C" in name:
                return name
        # 2. Fallback to any POS or 58mm printer
        for p in printers:
            name = p[2]
            if "POS" in name.upper() or "XP-58" in name:
                return name
        # 3. Last fallback: default
        return win32print.GetDefaultPrinter()
    except Exception:
        return ""


def print_raw_text(text: str):
    """Sends raw string directly to the thermal printer via win32print."""
    printer_name = get_printer_name()
    if not printer_name:
        raise Exception("No se pudo detectar ninguna impresora instalada.")

    # ESC/POS Commands
    # Initialize: ESC @
    # Cut paper: GS V 0
    init_cmd = b'\x1B\x40'
    cut_cmd = b'\x1D\x56\x00'

    # Encode latin characters cleanly
    try:
        raw_bytes = text.encode('cp850', errors='replace')
    except Exception:
        raw_bytes = text.encode('utf-8', errors='replace')

    full_data = init_cmd + raw_bytes + b'\n\n\n\n\n' + cut_cmd

    try:
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Recibo Llanos Core", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, full_data)
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
    except Exception as e:
        raise Exception(f"Fallo al comunicarse con la impresora '{printer_name}': {e}")


# ─── FORMATTERS ──────────────────────────────────────────────────────────────

def build_nota_text(data: dict) -> str:
    """Builds the plain-text layout for Nota de Entrega."""
    num = data.get('numero', '')
    fecha = data.get('fecha', '')
    hora = data.get('hora', '')
    cliente = data.get('cliente', '')[:WIDTH]
    telefono = data.get('telefono', '') or '—'
    ci = data.get('ci', '') or '—'
    obs = (data.get('observaciones', '') or '').replace('\n', ' ')

    lines = []
    lines.append(_center("LLANOS CORE"))
    lines.append(_center("SERVICIO TECNICO ESPECIALIZADO"))
    lines.append(_thick_line())
    lines.append(_center("NOTA DE ENTREGA"))
    lines.append(_center(f"N: {num}"))
    lines.append(_line())
    lines.append(_left_right(f"FECHA: {fecha}", f"HORA: {hora}"))
    lines.append(_line())
    lines.append("CLIENTE:")
    lines.append(cliente.upper())
    lines.append(f"TLF: {telefono}   CI: {ci}")
    lines.append(_thick_line())
    lines.append("ARTICULOS ENTREGADOS")
    lines.append(_line())
    
    items = json.loads(data.get('items_json', '[]') or '[]')
    total = data.get('total', 0.0)
    total_items = 0
    
    # Header for items with prices
    lines.append("CANT   DESCRIPCION          PRECIO    SUBTOTAL")
    lines.append(_line())
    
    for i, item in enumerate(items):
        desc_raw = item.get('descripcion', '').strip().upper()
        if not desc_raw: continue
        total_items += 1
        
        try:
            cant = int(item.get('cantidad', 1))
            precio = float(item.get('precio', 0.0))
            sub = cant * precio
        except ValueError:
            cant = 0; precio = 0.0; sub = 0.0
            
        # Wrap description (20 chars width)
        desc_lines = []
        curr = ""
        for w in desc_raw.split(' '):
            if len(curr) + len(w) + 1 <= 20:
                curr += (w + " ")
            else:
                desc_lines.append(curr.strip().ljust(20))
                curr = w + " "
        if curr: desc_lines.append(curr.strip().ljust(20))
        if not desc_lines: desc_lines = ["".ljust(20)]

        c_str = str(cant).ljust(4)
        p_str = f"${precio:.2f}".rjust(9)
        s_str = f"${sub:.2f}".rjust(10)
        
        # First line with all columns
        lines.append(f"{c_str} {desc_lines[0]} {p_str} {s_str}")
        # Other lines only description
        for extra_desc in desc_lines[1:]:
            lines.append(f"     {extra_desc}")
        
    lines.append(_thick_line())
    lines.append(_left_right("TOTAL ITEMS:", str(total_items)))
    
    total_str = f"${total:.2f}"
    lines.append(_left_right("TOTAL A PAGAR ($):", total_str).upper())
    lines.append(_thick_line())
    
    lines.append("DIAGNOSTICO / NOTAS:")
    words = obs.split(' ')
    curr_line = ""
    for w in words:
        if len(curr_line) + len(w) + 1 <= WIDTH:
            curr_line += (w + " ")
        else:
            if curr_line: lines.append(curr_line.strip())
            curr_line = w + " "
    if curr_line: lines.append(curr_line.strip())
    
    lines.append(_thick_line())
    lines.append("")
    lines.append("")
    lines.append(_center("_______________________"))
    lines.append(_center("FIRMA DEL CLIENTE"))
    lines.append("")
    lines.append(_center("Entregado por: LLANOS CORE"))
    lines.append(_line())
    lines.append(_center("Gracias por su preferencia!"))
    lines.append(_center(f"{num} - {fecha} {hora}"))
    
    return '\n'.join(lines)


def build_reporte_text(data: dict) -> str:
    """Builds the plain-text layout for Reporte de PC."""
    num = data.get('numero', '')
    fecha = data.get('fecha', '')
    hora = data.get('hora', '')
    cliente = data.get('cliente', '')[:WIDTH]
    telefono = data.get('telefono', '') or '—'
    ci = data.get('ci', '') or '—'
    marca = data.get('marca', '') or '—'
    modelo = data.get('modelo', '') or '—'
    serial = data.get('serial', '') or '—'
    diag = (data.get('diagnostico', '') or '').replace('\n', ' ')
    estado = data.get('estado', '').upper()
    costo = data.get('costo', '') or '—'

    lines = []
    lines.append(_center("LLANOS CORE"))
    lines.append(_center("SERVICIO TECNICO ESPECIALIZADO"))
    lines.append(_thick_line())
    lines.append(_center("REPORTE DE PC"))
    lines.append(_center(f"N: {num}"))
    lines.append(_line())
    lines.append(_left_right(f"FECHA: {fecha}", f"HORA: {hora}"))
    lines.append(_line())
    lines.append("CLIENTE:")
    lines.append(cliente.upper())
    lines.append(f"TLF: {telefono}   CI: {ci}")
    lines.append(_thick_line())
    lines.append("DATOS DEL EQUIPO")
    lines.append(f"MARCA : {marca.upper()}")
    lines.append(f"MODELO: {modelo.upper()}")
    lines.append(f"SERIAL: {serial.upper()}")
    lines.append(_thick_line())
    lines.append("DIAGNOSTICO TECNICO:")
    
    words = diag.split(' ')
    curr_line = ""
    for w in words:
        if len(curr_line) + len(w) + 1 <= WIDTH:
            curr_line += (w + " ")
        else:
            if curr_line: lines.append(curr_line.strip())
            curr_line = w + " "
    if curr_line: lines.append(curr_line.strip())
    
    lines.append(_thick_line())
    lines.append(_left_right("ESTADO:", estado))
    lines.append(_left_right("COSTO:", costo))
    lines.append(_thick_line())
    lines.append("")
    lines.append("")
    lines.append(_center("_______________________"))
    lines.append(_center("FIRMA DEL CLIENTE"))
    lines.append("")
    lines.append(_center("Tecnico Responsable: LLANOS CORE"))
    lines.append(_line())
    lines.append(_center("Gracias por confiar en nosotros!"))
    lines.append(_center(f"{num} - {fecha} {hora}"))
    
    return '\n'.join(lines)


def build_venta_text(data: dict) -> str:
    """Builds the plain-text layout for Ventas de Repuestos."""
    num = data.get('numero', '')
    fecha = data.get('fecha', '')
    hora = data.get('hora', '')
    cliente = data.get('cliente', '')[:WIDTH]
    telefono = data.get('telefono', '') or '—'
    ci = data.get('ci', '') or '—'
    
    items = data.get('items')
    if items is None:
        import json
        items = json.loads(data.get('items_json', '[]') or '[]')
        
    total = data.get('total', 0.0)

    lines = []
    lines.append(_center("LLANOS CORE"))
    lines.append(_center("VENTA DE REPUESTOS"))
    lines.append(_thick_line())
    lines.append(_center(f"FACTURA N: {num}"))
    lines.append(_line())
    lines.append(_left_right(f"FECHA: {fecha}", f"HORA: {hora}"))
    lines.append(_line())
    lines.append(f"CLIENTE:\n{cliente}")
    lines.append(f"TLF: {telefono}    CI: {ci}")
    lines.append(_thick_line())
    lines.append("CANT   DESCRIPCION          PRECIO    SUBTOTAL")
    lines.append(_line())
    
    # 6 cols para cant, 20 para desc, 10 precio, 10 subtotal = 46. Espacios = 48.
    for item in items:
        try:
            cant = int(item.get('cantidad', 1))
            precio = float(item.get('precio', 0.0))
            sub = cant * precio
        except ValueError:
            cant = 0
            precio = 0.0
            sub = 0.0
            
        # Wrap description
        desc_raw = item.get('descripcion', '').upper()
        desc_lines = []
        curr = ""
        # 20 is the column width for description
        for w in desc_raw.split(' '):
            if len(curr) + len(w) + 1 <= 20:
                curr += (w + " ")
            else:
                desc_lines.append(curr.strip().ljust(20))
                curr = w + " "
        if curr: desc_lines.append(curr.strip().ljust(20))
        if not desc_lines: desc_lines = ["".ljust(20)]

        c_str = str(cant).ljust(4)
        p_str = f"${precio:.2f}".rjust(9)
        s_str = f"${sub:.2f}".rjust(10)
        
        # First line with all columns
        lines.append(f"{c_str} {desc_lines[0]} {p_str} {s_str}")
        # Other lines only description
        for extra_desc in desc_lines[1:]:
            lines.append(f"     {extra_desc}")

    lines.append(_thick_line())
    
    total_str = f"${total:.2f}"
    lines.append(_left_right("TOTAL A PAGAR ($):", total_str).upper())
    lines.append(_thick_line())
    
    lines.append("\n\n")
    lines.append(_center("Gracias por su compra!"))
    lines.append(_center(f"{num} - {fecha} {hora}"))

    return '\n'.join(lines)


def build_venta_equipo_text(data: dict) -> str:
    """Builds the plain-text layout for Ventas de Equipos Completos."""
    num = data.get('numero', '')
    fecha = data.get('fecha', '')
    hora = data.get('hora', '')
    cliente = data.get('cliente', '')[:WIDTH]
    telefono = data.get('telefono', '') or '—'
    ci = data.get('ci', '') or '—'
    
    # Specs
    marca = data.get('marca', '')
    modelo = data.get('modelo', '')
    serial = data.get('serial', '')
    cpu = data.get('procesador', '')
    ram = data.get('ram', '')
    almacenamiento = data.get('almacenamiento', '')
    mother = data.get('tarjeta_madre', '')
    fuente = data.get('fuente_poder', '')
    so = data.get('so', '')
    gpu = data.get('grafica', '')
    dvd = data.get('dvd', '')
    teclado = data.get('teclado', '')
    mouse = data.get('mouse', '')
    cables = data.get('combo_cables', '')
    wifi = data.get('antena_wifi', '')
    
    total = data.get('total', 0.0)
    obs = data.get('observaciones', '')

    lines = []
    lines.append(_center("LLANOS CORE"))
    lines.append(_center("VENTA DE EQUIPO COMPLETO"))
    lines.append(_thick_line())
    lines.append(_center(f"FACTURA N: {num}"))
    lines.append(_line())
    lines.append(_left_right(f"FECHA: {fecha}", f"HORA: {hora}"))
    lines.append(_line())
    lines.append(f"CLIENTE:\n{cliente}")
    lines.append(f"TLF: {telefono}    CI: {ci}")
    lines.append(_thick_line())
    lines.append(_center("ESPECIFICACIONES DEL EQUIPO"))
    lines.append(_line())
    lines.append(f"MARCA:  {marca}")
    lines.append(f"MODELO: {modelo}")
    lines.append(f"SERIAL: {serial}")
    lines.append(_line())
    lines.append(f"CPU:    {cpu}")
    lines.append(f"RAM:    {ram}")
    lines.append(f"DISCO:  {almacenamiento}")
    lines.append(f"M.BOARD:{mother}")
    lines.append(f"FUENTE: {fuente}")
    lines.append(f"S.O.:   {so}")
    if gpu:     lines.append(f"GRAFICA:{gpu}")
    if dvd:     lines.append(f"DVD:    {dvd}")
    if teclado: lines.append(f"TECLADO:{teclado}")
    if mouse:   lines.append(f"MOUSE:  {mouse}")
    if cables:  lines.append(f"CABLES: {cables}")
    if wifi:    lines.append(f"WIFI:   {wifi}")
    
    lines.append(_thick_line())
    
    total_str = f"${total:.2f}"
    lines.append(_left_right("PRECIO DEL EQUIPO ($):", total_str).upper())
    lines.append(_thick_line())

    
    if obs:
        lines.append("")
        lines.append("GARANTIA / CONDICIONES:")
        words = obs.split()
        curr_line = ""
        for w in words:
            if len(curr_line) + len(w) + 1 <= WIDTH:
                curr_line += w + " "
            else:
                lines.append(curr_line.strip())
                curr_line = w + " "
        if curr_line: lines.append(curr_line.strip())
        lines.append("")
    
    lines.append("\n\n")
    lines.append(_center("Gracias por su compra!"))
    lines.append(_center(f"{num} - {fecha} {hora}"))

    return '\n'.join(lines)

