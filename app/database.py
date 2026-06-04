import sqlite3
import os

def get_db():
    # En Render usaremos una ruta absoluta al volumen persistente (ej: /data/recetas.db)
    # Localmente usaremos la ruta relativa de siempre.
    db_path = os.environ.get('DATABASE_URL', 'db/recetas.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn