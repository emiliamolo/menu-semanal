import sqlite3
import csv
import os
def init_db():
    # 0. Eliminar la base de datos anterior si existe para empezar de cero
    db_path = 'db/recetas.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    # 1. Conectar (creará el archivo recetas.db nuevo)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 2. Ejecutar el script .sql para crear las tablas
    with open('db/schema.sql', 'r') as f:
        cursor.executescript(f.read())

    # 3. Cargar datos desde el CSV
    with open('recetas.csv', 'r', encoding='utf-8') as f:
        # DictReader es útil si el CSV tiene encabezados
        lector_csv = csv.DictReader(f) 
        for fila in lector_csv:
            if fila['comida'] != None and fila['tiempo'] != None:
                cursor.execute('''
                    INSERT INTO recetas (nombre, tiempo, tipo, comida, instrucciones, image_ruta, publica)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (fila['nombre'], int(fila['tiempo']), fila['tipo'], fila['comida'], fila["instrucciones"], fila.get('image_ruta'), 1))
                id_receta = cursor.lastrowid
                for ingrediente in fila['ingredientes'].split(','):
                    cursor.execute("INSERT OR IGNORE INTO ingredientes (nombre) VALUES (?)", (ingrediente,))
                    cursor.execute(
                        "SELECT id_ingrediente FROM ingredientes WHERE nombre = ?",
                        (ingrediente,)
                    )
                    id_ingrediente = cursor.fetchone()[0]
                    cursor.execute("INSERT INTO ingrediente_receta (id_ingrediente, id_receta) VALUES (?, ?)", (id_ingrediente, id_receta))
    conn.commit()
    conn.close()
    print("Base de datos creada y recetas cargadas con éxito.")

init_db()