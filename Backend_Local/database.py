import sqlite3
import json
import os
import base64
import urllib.request
import requests
from datetime import datetime

# Ruta absoluta para asegurar que funcione en el Backend_Local
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'llanos_core.db')
FIREBASE_URL = "https://llanos-core-gestion-docmentos-default-rtdb.firebaseio.com/registros"


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    # Optimization: Write-Ahead Logging for better concurrency
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas_entrega (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            numero      TEXT    UNIQUE NOT NULL,
            fecha       TEXT    NOT NULL,
            hora        TEXT    NOT NULL,
            cliente     TEXT    NOT NULL,
            telefono    TEXT    DEFAULT '',
            ci          TEXT    DEFAULT '',
            items_json  TEXT    DEFAULT '[]',
            total       REAL    DEFAULT 0.0,
            observaciones TEXT  DEFAULT '',
            marca       TEXT    DEFAULT '',
            modelo      TEXT    DEFAULT '',
            serial      TEXT    DEFAULT '',
            procesador  TEXT    DEFAULT '',
            ram         TEXT    DEFAULT '',
            almacenamiento TEXT DEFAULT '',
            tarjeta_madre  TEXT    DEFAULT '',
            fuente_poder   TEXT    DEFAULT '',
            so             TEXT    DEFAULT '',
            grafica        TEXT    DEFAULT '',
            dvd            TEXT    DEFAULT '',
            teclado        TEXT    DEFAULT '',
            mouse          TEXT    DEFAULT '',
            combo_cables   TEXT    DEFAULT '',
            antena_wifi    TEXT    DEFAULT '',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reportes_pc (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            numero      TEXT    UNIQUE NOT NULL,
            fecha       TEXT    NOT NULL,
            hora        TEXT    NOT NULL,
            cliente     TEXT    NOT NULL,
            telefono    TEXT    DEFAULT '',
            ci          TEXT    DEFAULT '',
            marca       TEXT    DEFAULT '',
            modelo      TEXT    DEFAULT '',
            serial      TEXT    DEFAULT '',
            diagnostico TEXT    DEFAULT '',
            estado      TEXT    DEFAULT 'En Revisión',
            costo       TEXT    DEFAULT '',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas_repuestos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            numero      TEXT    UNIQUE NOT NULL,
            fecha       TEXT    NOT NULL,
            hora        TEXT    NOT NULL,
            cliente     TEXT    NOT NULL,
            telefono    TEXT    DEFAULT '',
            ci          TEXT    DEFAULT '',
            items_json  TEXT    DEFAULT '[]',
            total       REAL    DEFAULT 0.0,
            observaciones TEXT  DEFAULT '',
            marca       TEXT    DEFAULT '',
            modelo      TEXT    DEFAULT '',
            serial      TEXT    DEFAULT '',
            procesador  TEXT    DEFAULT '',
            ram         TEXT    DEFAULT '',
            almacenamiento TEXT DEFAULT '',
            tarjeta_madre  TEXT    DEFAULT '',
            fuente_poder   TEXT    DEFAULT '',
            so             TEXT    DEFAULT '',
            grafica        TEXT    DEFAULT '',
            dvd            TEXT    DEFAULT '',
            teclado        TEXT    DEFAULT '',
            mouse          TEXT    DEFAULT '',
            combo_cables   TEXT    DEFAULT '',
            antena_wifi    TEXT    DEFAULT '',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas_equipos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            numero      TEXT    UNIQUE NOT NULL,
            fecha       TEXT    NOT NULL,
            hora        TEXT    NOT NULL,
            cliente     TEXT    NOT NULL,
            telefono    TEXT    DEFAULT '',
            ci          TEXT    DEFAULT '',
            marca       TEXT    DEFAULT '',
            modelo      TEXT    DEFAULT '',
            serial      TEXT    DEFAULT '',
            procesador  TEXT    DEFAULT '',
            ram         TEXT    DEFAULT '',
            almacenamiento TEXT DEFAULT '',
            tarjeta_madre  TEXT    DEFAULT '',
            fuente_poder   TEXT    DEFAULT '',
            so             TEXT    DEFAULT '',
            grafica        TEXT    DEFAULT '',
            dvd            TEXT    DEFAULT '',
            teclado        TEXT    DEFAULT '',
            mouse          TEXT    DEFAULT '',
            combo_cables   TEXT    DEFAULT '',
            antena_wifi    TEXT    DEFAULT '',
            items_json  TEXT    DEFAULT '[]',
            total       REAL    DEFAULT 0.0,
            observaciones TEXT  DEFAULT '',
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key         TEXT PRIMARY KEY,
            value       TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('exchange_rate', '45.50')")
    
    # Optimization: Indexes for faster searching in history views
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notas_cliente ON notas_entrega(cliente)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notas_numero ON notas_entrega(numero)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_repuestos_cliente ON ventas_repuestos(cliente)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_repuestos_numero ON ventas_repuestos(numero)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reportes_cliente ON reportes_pc(cliente)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipos_cliente ON ventas_equipos(cliente)")

    # Tabla de Clientes para auto-completado
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ci TEXT UNIQUE,
            nombre TEXT,
            telefono TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_ci ON clientes(ci)")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cloud_nombre ON cloud_registrations(nombre)")

    # Tabla para registros automáticos desde la nube
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cloud_registrations (
            id TEXT PRIMARY KEY,
            nombre TEXT,
            telefono TEXT,
            ci TEXT,
            equipo TEXT,
            serial TEXT,
            falla TEXT,
            fecha TEXT,
            status TEXT DEFAULT 'nuevo'
        )
    """)

    # Migración: Añadir columnas si no existen (para bases de datos ya creadas)
    for table in ["notas_entrega", "ventas_repuestos"]:
        cols = [
            "marca", "modelo", "serial", "procesador", "ram", "almacenamiento",
            "tarjeta_madre", "fuente_poder", "so", "grafica", "dvd", "teclado",
            "mouse", "combo_cables", "antena_wifi"
        ]
        for col in cols:
            try: cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} TEXT DEFAULT ''")
            except: pass

    conn.commit()
    conn.close()


# ─── NOTAS DE ENTREGA ────────────────────────────────────────────────────────

def get_next_nota_number():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS cnt FROM notas_entrega')
    count = cursor.fetchone()['cnt']
    conn.close()
    return f'NE-{count + 1:04d}'


def save_nota(data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO notas_entrega
            (numero, fecha, hora, cliente, telefono, ci, items_json, total, observaciones,
             marca, modelo, serial, procesador, ram, almacenamiento, tarjeta_madre, 
             fuente_poder, so, grafica, dvd, teclado, mouse, combo_cables, antena_wifi)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        data['numero'], data['fecha'], data['hora'],
        data['cliente'], data['telefono'], data['ci'],
        data['items_json'], data['total'], data['observaciones'],
        data.get('marca',''), data.get('modelo',''), data.get('serial',''),
        data.get('procesador',''), data.get('ram',''), data.get('almacenamiento',''),
        data.get('tarjeta_madre',''), data.get('fuente_poder',''), data.get('so',''),
        data.get('grafica',''), data.get('dvd',''), data.get('teclado',''),
        data.get('mouse',''), data.get('combo_cables',''), data.get('antena_wifi','')
    ))
    row_id = cursor.lastrowid
    conn.commit()
    save_or_update_cliente(data.get('ci'), data.get('cliente'), data.get('telefono'))
    conn.close()
    return row_id


def get_all_notas(search: str = ''):
    conn = get_connection()
    cursor = conn.cursor()
    if search:
        cursor.execute(
            'SELECT * FROM notas_entrega WHERE cliente LIKE ? OR numero LIKE ? ORDER BY id DESC',
            (f'%{search}%', f'%{search}%')
        )
    else:
        cursor.execute('SELECT * FROM notas_entrega ORDER BY id DESC')
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_nota_by_id(nota_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notas_entrega WHERE id = ?', (nota_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_nota(nota_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notas_entrega WHERE id = ?', (nota_id,))
    conn.commit()
    conn.close()


# ─── REPORTES PC ─────────────────────────────────────────────────────────────

def get_next_reporte_number():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS cnt FROM reportes_pc')
    count = cursor.fetchone()['cnt']
    conn.close()
    return f'RP-{count + 1:04d}'


def save_reporte(data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO reportes_pc
            (numero, fecha, hora, cliente, telefono, ci,
             marca, modelo, serial, diagnostico, estado, costo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['numero'], data['fecha'], data['hora'],
        data['cliente'], data['telefono'], data['ci'],
        data['marca'], data['modelo'], data['serial'],
        data['diagnostico'], data['estado'], data['costo']
    ))
    row_id = cursor.lastrowid
    conn.commit()
    save_or_update_cliente(data.get('ci'), data.get('cliente'), data.get('telefono'))
    conn.close()
    return row_id


def get_all_reportes(search: str = ''):
    conn = get_connection()
    cursor = conn.cursor()
    if search:
        cursor.execute(
            '''SELECT * FROM reportes_pc
               WHERE cliente LIKE ? OR numero LIKE ? OR estado LIKE ?
               ORDER BY id DESC''',
            (f'%{search}%', f'%{search}%', f'%{search}%')
        )
    else:
        cursor.execute('SELECT * FROM reportes_pc ORDER BY id DESC')
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_reporte_by_id(reporte_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reportes_pc WHERE id = ?', (reporte_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_reporte_estado(reporte_id: int, estado: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE reportes_pc SET estado = ? WHERE id = ?', (estado, reporte_id))
    conn.commit()
    conn.close()


def delete_reporte(reporte_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM reportes_pc WHERE id = ?', (reporte_id,))
    conn.commit()
    conn.close()


# ─── VENTAS DE REPUESTOS ─────────────────────────────────────────────────────

def get_next_venta_number():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS cnt FROM ventas_repuestos')
    count = cursor.fetchone()['cnt']
    conn.close()
    return f'VR-{count + 1:04d}'


def save_venta(data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO ventas_repuestos
            (numero, fecha, hora, cliente, telefono, ci, items_json, total, observaciones,
             marca, modelo, serial, procesador, ram, almacenamiento, tarjeta_madre, 
             fuente_poder, so, grafica, dvd, teclado, mouse, combo_cables, antena_wifi)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        data['numero'], data['fecha'], data['hora'],
        data['cliente'], data['telefono'], data['ci'],
        data['items_json'], data['total'], data['observaciones'],
        data.get('marca',''), data.get('modelo',''), data.get('serial',''),
        data.get('procesador',''), data.get('ram',''), data.get('almacenamiento',''),
        data.get('tarjeta_madre',''), data.get('fuente_poder',''), data.get('so',''),
        data.get('grafica',''), data.get('dvd',''), data.get('teclado',''),
        data.get('mouse',''), data.get('combo_cables',''), data.get('antena_wifi','')
    ))
    row_id = cursor.lastrowid
    conn.commit()
    save_or_update_cliente(data.get('ci'), data.get('cliente'), data.get('telefono'))
    conn.close()
    return row_id


def get_all_ventas(search: str = ''):
    conn = get_connection()
    cursor = conn.cursor()
    if search:
        cursor.execute(
            'SELECT * FROM ventas_repuestos WHERE cliente LIKE ? OR numero LIKE ? ORDER BY id DESC',
            (f'%{search}%', f'%{search}%')
        )
    else:
        cursor.execute('SELECT * FROM ventas_repuestos ORDER BY id DESC')
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_venta_by_id(venta_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ventas_repuestos WHERE id = ?', (venta_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_venta(venta_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ventas_repuestos WHERE id = ?', (venta_id,))
    conn.commit()
    conn.close()


# ─── VENTAS DE EQUIPOS COMPLETOS ─────────────────────────────────────────────

def get_next_venta_equipo_number():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS cnt FROM ventas_equipos')
    count = cursor.fetchone()['cnt']
    conn.close()
    return f'VE-{count + 1:04d}'


def save_venta_equipo(data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO ventas_equipos
            (numero, fecha, hora, cliente, telefono, ci, marca, modelo, serial, procesador, ram, almacenamiento, 
             tarjeta_madre, fuente_poder, so, grafica, dvd, teclado, mouse, combo_cables, antena_wifi,
             items_json, total, observaciones)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        data['numero'], data['fecha'], data['hora'],
        data['cliente'], data['telefono'], data['ci'],
        data['marca'], data['modelo'], data['serial'],
        data['procesador'], data['ram'], data['almacenamiento'],
        data['tarjeta_madre'], data['fuente_poder'], data['so'],
        data['grafica'], data['dvd'], data['teclado'], data['mouse'],
        data['combo_cables'], data['antena_wifi'],
        data['items_json'], data['total'], data['observaciones']
    ))
    row_id = cursor.lastrowid
    conn.commit()
    save_or_update_cliente(data.get('ci'), data.get('cliente'), data.get('telefono'))
    conn.close()
    return row_id


def get_all_ventas_equipos(search: str = ''):
    conn = get_connection()
    cursor = conn.cursor()
    if search:
        cursor.execute(
            'SELECT * FROM ventas_equipos WHERE cliente LIKE ? OR numero LIKE ? ORDER BY id DESC',
            (f'%{search}%', f'%{search}%')
        )
    else:
        cursor.execute('SELECT * FROM ventas_equipos ORDER BY id DESC')
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_venta_equipo_by_id(id_venta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ventas_equipos WHERE id = ?', (id_venta,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_venta_equipo(id_venta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ventas_equipos WHERE id = ?", (id_venta,))
    conn.commit()


# ── CLIENTES LOGIC ────────────────────────────────────────────────────────

def save_or_update_cliente(ci, nombre, telefono):
    if not ci or not nombre: return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO clientes (ci, nombre, telefono)
        VALUES (?, ?, ?)
        ON CONFLICT(ci) DO UPDATE SET
            nombre = excluded.nombre,
            telefono = excluded.telefono
    ''', (ci, nombre, telefono))
    conn.commit()


def get_cliente_by_name(nombre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ci, telefono FROM clientes WHERE nombre LIKE ? LIMIT 1", (f"%{nombre}%",))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'ci': row[0], 'telefono': row[1]}
    return None


def search_cloud_registration(nombre):
    """Busca en los datos que llegaron por el link del cliente."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cloud_registrations WHERE nombre LIKE ? LIMIT 1", (f"%{nombre}%",))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_cliente_by_ci(ci):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, telefono FROM clientes WHERE ci = ?", (ci,))
    row = cursor.fetchone()
    if row:
        return {'nombre': row[0], 'telefono': row[1]}
    return None


def get_all_clientes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ci, nombre, telefono FROM clientes ORDER BY nombre")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_exchange_rate() -> float:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'exchange_rate'")
        row = cursor.fetchone()
        conn.close()
        return float(row[0]) if row else 45.50
    except:
        return 45.50


def set_exchange_rate(rate: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('exchange_rate', ?)", (str(rate),))
    conn.commit()
    conn.close()


# ── CLOUD SYNC ────────────────────────────────────────────────────────────

def sincronizar_nube():
    """Descarga datos de Firebase, los guarda localmente y limpia la nube."""
    print("📡 Sincronizando con la nube...")
    try:
        response = requests.get(f"{FIREBASE_URL}.json")
        data = response.json()
        
        if not data:
            print("✅ Nube vacía. No hay registros nuevos.")
            return 0
            
        conn = get_connection()
        cursor = conn.cursor()
        nuevos = 0
        
        for fb_id, reg in data.items():
            if not isinstance(reg, dict) or fb_id == "error":
                continue
            try:
                ci = reg.get('ci') or reg.get('c')
                nombre = reg.get('nombre') or reg.get('n')
                telefono = reg.get('telefono') or reg.get('t')
                if not ci or not nombre: continue
                cursor.execute("""
                    INSERT OR REPLACE INTO clientes (ci, nombre, telefono) 
                    VALUES (?, ?, ?)
                """, (ci, nombre, telefono))
                equipo = reg.get('equipo') or reg.get('e')
                serial = reg.get('serial') or reg.get('s')
                falla = reg.get('falla') or reg.get('f')
                fecha = reg.get('fecha') or reg.get('ts')
                cursor.execute("""
                    INSERT OR IGNORE INTO cloud_registrations 
                    (id, nombre, telefono, ci, equipo, serial, falla, fecha)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (fb_id, nombre, telefono, ci, equipo, serial, falla, fecha))
                requests.delete(f"{FIREBASE_URL}/{fb_id}.json")
                nuevos += 1
            except Exception as e:
                print(f"⚠️ Error procesando registro {fb_id}: {e}")
        conn.commit()
        conn.close()
        print(f"✨ Sincronización exitosa: {nuevos} registros importados.")
        return nuevos
    except Exception as e:
        print(f"❌ Error de conexión con Firebase: {e}")
        return 0


def sync_cloud_registrations():
    return sincronizar_nube()


def get_new_cloud_registrations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cloud_registrations WHERE status = 'nuevo' ORDER BY fecha DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def mark_cloud_registration_read(reg_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE cloud_registrations SET status = 'leido' WHERE id = ?", (reg_id,))
    conn.commit()
    conn.close()
