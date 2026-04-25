import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'llanos_core.db')

def migrate():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    columns = [
        ('teclado', 'TEXT DEFAULT ""'),
        ('mouse', 'TEXT DEFAULT ""'),
        ('combo_cables', 'TEXT DEFAULT ""'),
        ('antena_wifi', 'TEXT DEFAULT ""')
    ]
    
    for col_name, col_type in columns:
        try:
            print(f"Adding column {col_name} to ventas_equipos...")
            cursor.execute(f"ALTER TABLE ventas_equipos ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            print(f"Column {col_name} already exists or error occurred.")
            
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
