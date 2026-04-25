import sqlite3
import os

db_path = 'c:/Users/Usuario para program/Documents/Proyecto/llanos_core.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('PRAGMA table_info(notas_entrega)')
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'total' not in columns:
        print("Adding column total to notas_entrega...")
        cursor.execute("ALTER TABLE notas_entrega ADD COLUMN total REAL DEFAULT 0.0")
            
    conn.commit()
    conn.close()
    print("Migration finished successfully.")
else:
    print("Database not found.")
