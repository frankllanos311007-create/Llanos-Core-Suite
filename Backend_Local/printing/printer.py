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
        for p in printers:
            name = p[2]
            if "XP-80C" in name:
                return name
        for p in printers:
            name = p[2]
            if "POS" in name.upper() or "XP-58" in name:
                return name
        return win32print.GetDefaultPrinter()
    except Exception:
        return ""


def print_raw_text(text: str):
    """Sends raw string directly to the thermal printer via win32print."""
    printer_name = get_printer_name()
    if not printer_name:
        raise Exception("No se pudo detectar ninguna impresora instalada.")

    init_cmd = b'\x1B\x40'
    cut_cmd = b'\x1D\x56\x00'

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

def _add_specs_to_lines(lines: list, data: dict):
    """Helper to add technical specs to the lines list."""
    marca = data.get('marca', '')
    modelo = data.get('modelo', '')
    serial = data.get('serial', '')
    cpu = data.get('procesador', '')
    ram = data.get('ram', '')
    disco = data.get('almacenamiento', '')
    mother = data.get('tarjeta_madre', '')
    fuente = data.get('fuente_poder', '')
    so = data.get('so', '')
    gpu = data.get('grafica', '')
    dvd = data.get('dvd', '')
    teclado = data.get('teclado', '')
    mouse = data.get('mouse', '')
    cables = data.get('combo_cables', '')
    wifi = data.get('antena_wifi', '')

    if marca:  lines.append(f"MARCA:   {marca}")
    if modelo: lines.append(f"MODELO:  {modelo}")
    if serial: lines.append(f"SERIAL:  {serial}")
    if cpu or ram or disco: lines.append(_line())
    if cpu:    lines.append(f"CPU:     {cpu}")
    if ram:    lines.append(f"RAM:     {ram}")
    if disco:  lines.append(f"DISCO:   {disco}")
    if mother or fuente or so: lines.append(_line())
    if mother: lines.append(f"M.BOARD: {mother}")
    if fuente: lines.append(f"FUENTE:  {fuente}")
    if so:     lines.append(f"S.O.:    {so}")
    if gpu or dvd or teclado or mouse or cables or wifi: lines.append(_line())
    if gpu:     lines.append(f"GRAFICA: {gpu}")
    if dvd:     lines.append(f"DVD:     {dvd}")
    if teclado: lines.append(f"TECLADO: {teclado}")
    if mouse:   lines.append(f"MOUSE:   {mouse}")
    if cables:  lines.append(f"CABLES:  {cables}")
    if wifi:    lines.append(f"WIFI:    {wifi}")

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
    lines.append(_center("ESPECIFICACIONES DEL EQUIPO"))
    lines.append(_line())
    
    _add_specs_to_lines(lines, data)
    
    lines.append(_thick_line())
    total_str = f"${data.get('total', 0.0):.2f}"
    lines.append(_left_right("TOTAL A PAGAR ($):", total_str).upper())
    lines.append(_thick_line())
    
    if obs:
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
    obs = data.get('observaciones', '')

    lines = []
    lines.append(_center("LLANOS CORE"))
    lines.append(_center("VENTA DE REPUESTOS / EQUIPOS"))
    lines.append(_thick_line())
    lines.append(_center(f"FACTURA N: {num}"))
    lines.append(_line())
    lines.append(_left_right(f"FECHA: {fecha}", f"HORA: {hora}"))
    lines.append(_line())
    lines.append(f"CLIENTE:\n{cliente}")
    lines.append(f"TLF: {telefono}    CI: {ci}")
    lines.append(_thick_line())
    lines.append(_center("DETALLES TECNICOS"))
    lines.append(_line())
    
    _add_specs_to_lines(lines, data)

    lines.append(_thick_line())
    total_str = f"${data.get('total', 0.0):.2f}"
    lines.append(_left_right("TOTAL A PAGAR ($):", total_str).upper())
    lines.append(_thick_line())
    
    if obs:
        lines.append("OBSERVACIONES:")
        lines.append(obs)
        lines.append(_line())

    lines.append("\n\n")
    lines.append(_center("Gracias por su compra!"))
    lines.append(_center(f"{num} - {fecha} {hora}"))
    return '\n'.join(lines)


def build_venta_equipo_text(data: dict) -> str:
    """Alias for consistency, uses the same layout as nota but for equipment sale."""
    return build_venta_text(data)
