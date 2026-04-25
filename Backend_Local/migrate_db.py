import sqlite3
import os

db_path = 'c:/Users/Usuario para program/Documents/Proyecto/llanos_core.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('PRAGMA table_info(ventas_equipos)')
    columns = [row[1] for row in cursor.fetchall()]
    
    new_cols = [
        ('tarjeta_madre', 'TEXT DEFAULT ""'),
        ('fuente_poder', 'TEXT DEFAULT ""'),
        ('so', 'TEXT DEFAULT ""'),
        ('grafica', 'TEXT DEFAULT ""'),
        ('dvd', 'TEXT DEFAULT ""')
    ]
    
    for col_name, col_type in new_cols:
        if col_name not in columns:
            print(f"Adding column {col_name}...")
            cursor.execute(f"ALTER TABLE ventas_equipos ADD COLUMN {col_name} {col_type}")
            
    conn.commit()
    conn.close()
    print("Migration finished successfully.")
else:
    print("Database not found.")
