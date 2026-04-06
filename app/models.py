from app.database import get_db
from datetime import datetime
def obtener_receta_aleatoria(tipos, comida):
    if comida == "almuerzo": comida = "cena"
    db = get_db()
    # Aseguramos que tipos sea una lista (por si viene un solo string)
    if not isinstance(tipos, list): 
        tipos = [tipos] if tipos else []
        
    placeholders = ",".join(["?"] * len(tipos))
    
    if not tipos:
        query = "SELECT * FROM recetas WHERE comida = ? ORDER BY RANDOM() LIMIT 1"
        params = (comida,)
    else:
        query = f"SELECT * FROM recetas WHERE tipo IN ({placeholders}) AND comida = ? ORDER BY RANDOM() LIMIT 1"
        params = tuple(tipos) + (comida,)
    
    receta = db.execute(query, params).fetchone()
    db.close()
    return receta

def obtener_menu_aleatorio(tipos):
    db = get_db()
    if not tipos:
        tipos = ['V', 'G', 'C']
    placeholders = ",".join(["?"] * len(tipos))
    # Obtenemos 7 desayunos aleatorios
    query = f"SELECT * FROM recetas WHERE comida = 'desayuno' AND tipo IN ({placeholders}) ORDER BY RANDOM() LIMIT 7"
    params = tuple(tipos)
    desayunos = db.execute(query, params).fetchall()
    
    # Obtenemos 14 para cubrir almuerzo y cena de la semana
    query = f"SELECT * FROM recetas WHERE (comida = 'cena' OR comida = 'almuerzo') AND tipo IN ({placeholders}) ORDER BY RANDOM() LIMIT 14"
    cenas = db.execute(query, params).fetchall()
    
    db.close()
    print([d["nombre"] for d in desayunos])
    if (len(desayunos) != 7 or len(cenas) != 14): return None
    return desayunos, cenas

def guardar_menu(desayunos, cenas, id_usuario):
    db = get_db()
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # 1. Crear el encabezado del menú
        cursor = db.execute(
            "INSERT INTO menus (id_usuario, fecha) VALUES (?, ?)",
            (id_usuario, fecha_hoy)
        )
        id_menu = cursor.lastrowid

        # 3. Insertar cada relación en la tabla intermedia
        for i in range(len(desayunos)):
            db.execute(
                "INSERT INTO menu_receta (id_menu, id_receta, nro_dia) VALUES (?, ?, ?)",
                (id_menu, desayunos[i]['id_receta'], i)
            )
        for i in range(len(cenas)):
            db.execute(
                "INSERT INTO menu_receta (id_menu, id_receta, nro_dia) VALUES (?, ?, ?)",
                (id_menu, cenas[i]['id_receta'], i+7)
            )
        db.commit()
        return True
    except Exception as e:
        print(f"Error al guardar el menú relacional: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def get_user(nombre_usuario):
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE nombre = ?", (nombre_usuario,)).fetchone()
    db.close()
    return user
def check_mail(mail):
    db = get_db()
    mail_db = db.execute("SELECT * FROM usuarios WHERE mail = ?", (mail,)).fetchone()
    db.close()
    return mail_db

def get_user_info(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (user_id,)).fetchone()
    db.close()
    return user

def actualizar_contraseña(user_id, new_hash):
    db = get_db()
    try:
        db.execute("UPDATE usuarios SET hash = ?, reset_token = NULL WHERE id_usuario = ?", (new_hash, user_id))
        db.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar la contraseña: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def insert_user(user, hash_password, mail):
    db = get_db()
    try:
        cursor = db.execute("INSERT INTO usuarios(nombre, hash, mail) VALUES(?, ?, ?)", (user, hash_password, mail))
        db.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error al guardar: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def get_menus(id_usuario):
    db = get_db()
    
    menus_row = db.execute(
        "SELECT * FROM menus WHERE id_usuario = ? ORDER BY fecha DESC, id_menu DESC",
        (id_usuario,)
    ).fetchall()
    db.close()
    return menus_row

def get_recetas_for_user(id_usuario, privadas):
    db = get_db()
    sql = "SELECT * FROM recetas WHERE id_usuario = ?"
    if not privadas:
        sql += " AND publica = 1"
    sql += " ORDER BY id_receta DESC"
    recetas_row = db.execute(sql, (id_usuario,)
    ).fetchall()
    db.close()
    return recetas_row

def get_recetas_favoritas(user_id):
    db = get_db()
    
    recetas_row = db.execute(
        """
        SELECT r.*
        FROM recetas r
        JOIN preferidas p ON r.id_receta = p.id_receta
        WHERE p.id_usuario = ? 
        ORDER BY r.id_receta DESC
        """,
        (user_id,)
    ).fetchall()
    db.close()
    return recetas_row

def obtener_datos_menu(id_usuario, id_menu):
    """Busca el menú del usuario y trae todas sus recetas."""
    db = get_db()
    
    check = db.execute(
        "SELECT id_menu FROM menus WHERE id_usuario = ? AND id_menu = ?",
        (id_usuario, id_menu)
    ).fetchone()

    if not check:
        db.close()
        return None


    recetas = db.execute("""
            SELECT r.*, mr.nro_dia 
            FROM recetas r 
            JOIN menu_receta mr ON r.id_receta = mr.id_receta 
            WHERE mr.id_menu = ?
            ORDER BY mr.nro_dia ASC
        """, (id_menu,)).fetchall()
    db.close()

    desayunos = recetas[0:7]
    cenas = recetas[7:21]
    return {"desayunos": desayunos,
            "cenas": cenas,
            "ingredientes": obtener_lista_compras(id_menu)}


def obtener_datos_menu_usuario(id_usuario):
    """Busca el último menú del usuario y trae todas sus recetas."""
    db = get_db()
    
    menu_row = db.execute(
        "SELECT id_menu FROM menus WHERE id_usuario = ? ORDER BY fecha DESC, id_menu DESC LIMIT 1",
        (id_usuario,)
    ).fetchone()

    if not menu_row:
        db.close()
        return None

    id_menu = menu_row['id_menu']

    recetas = db.execute("""
            SELECT r.*, mr.nro_dia 
            FROM recetas r 
            JOIN menu_receta mr ON r.id_receta = mr.id_receta 
            WHERE mr.id_menu = ?
            ORDER BY mr.nro_dia ASC
        """, (id_menu,)).fetchall()
    db.close()

    desayunos = [r for r in recetas if r["comida"].lower() == "desayuno"]
    cenas = [r for r in recetas if r["comida"].lower() == "cena"]

    return {"desayunos": desayunos,
            "cenas": cenas,
            "ingredientes": obtener_lista_compras(id_menu)}


def obtener_lista_compras(id_menu):
    db = get_db()
    query = """
        SELECT DISTINCT i.nombre FROM ingredientes i
        JOIN ingrediente_receta ir ON i.id_ingrediente = ir.id_ingrediente
        JOIN recetas r ON r.id_receta = ir.id_receta
        JOIN menu_receta mr ON r.id_receta = mr.id_receta
        WHERE mr.id_menu = ?
    """
    rows = db.execute(query, (id_menu,)).fetchall()
    db.close()
    
    # Procesar strings de ingredientes para que no haya duplicados
    compras = [row["nombre"].capitalize() for row in rows]
    
    return sorted(list(compras))

def insertar_receta(datos_receta):
    db = get_db()
    
    try:
        cursor = db.execute("""
            INSERT INTO recetas (nombre, tiempo, tipo, comida, instrucciones, id_usuario, publica, precio_estimado, image_ruta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (datos_receta["nombre"], 
              datos_receta["tiempo"], 
              datos_receta["tipo"], 
              datos_receta["comida"], 
              datos_receta["instrucciones"], 
              datos_receta["id_usuario"], 
              datos_receta["publica"],
              datos_receta["precio_estimado"],
              datos_receta["image_ruta"]))

        id_nueva_receta = cursor.lastrowid

        for i in datos_receta["ingredientes"]:
            i.strip().lower()
            db.execute("INSERT OR IGNORE INTO ingredientes (nombre) VALUES (?)", (i,))
            id_ingrediente = db.execute("SELECT id_ingrediente FROM ingredientes WHERE nombre = ?", (i,)).fetchone()["id_ingrediente"]
            db.execute("INSERT INTO ingrediente_receta (id_receta, id_ingrediente) VALUES (?, ?)", 
                       (id_nueva_receta , id_ingrediente))
        db.commit()
        return True
    except Exception as e:
        print(f"Error al insertar receta: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def editar_receta(datos_receta):
    db = get_db()
    
    try:
        db.execute("""
            UPDATE recetas 
            SET nombre = ?, tiempo = ?, tipo = ?, comida = ?, instrucciones = ?, 
                   publica = ?, precio_estimado = ?, image_ruta = ?
            WHERE id_receta = ?
        """, (datos_receta["nombre"], 
              datos_receta["tiempo"], 
              datos_receta["tipo"], 
              datos_receta["comida"], 
              datos_receta["instrucciones"], 
              datos_receta["publica"],
              datos_receta["precio_estimado"],
              datos_receta["image_ruta"],
              datos_receta["id_receta"]))

        db.execute("DELETE FROM ingrediente_receta WHERE id_receta = ?", (datos_receta["id_receta"],))

        for i in datos_receta["ingredientes"]:
            i.strip().lower()
            db.execute("INSERT OR IGNORE INTO ingredientes (nombre) VALUES (?)", (i,))
            id_ingrediente = db.execute("SELECT id_ingrediente FROM ingredientes WHERE nombre = ?", (i,)).fetchone()["id_ingrediente"]
            db.execute("INSERT INTO ingrediente_receta (id_receta, id_ingrediente) VALUES (?, ?)", 
                       (datos_receta["id_receta"], id_ingrediente))
        db.commit()
        return True
    except Exception as e:
        print(f"Error al editar receta: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def get_receta(id_receta):
    db = get_db()
    receta = db.execute("SELECT * FROM recetas WHERE id_receta = ?", (id_receta,)).fetchone()
    ingredientes = db.execute("""SELECT nombre FROM ingredientes i
                                JOIN ingrediente_receta ir ON i.id_ingrediente = ir.id_ingrediente
                                WHERE ir.id_receta = ?
                              """, (id_receta,)).fetchall()
    db.close()
    ingredientes = [row["nombre"] for row in ingredientes]
    return receta, ingredientes

def delete_menu(id_menu, id_usuario):
    db = get_db()

    try:
        cursor = db.execute(
            "DELETE FROM menus WHERE id_menu = ? AND id_usuario = ?",
            (id_menu, id_usuario)
        )
        if cursor.rowcount == 0: return False
        db.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar menu: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def delete_receta(id_receta, id_usuario):
    db = get_db()

    try:
        cursor = db.execute(
            "DELETE FROM recetas WHERE id_receta = ? AND id_usuario = ?",
            (id_receta, id_usuario)
        )
        if cursor.rowcount == 0: return False
        db.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar menu: {e}")
        db.rollback()
        return False
    finally:
        db.close()

from datetime import datetime, timedelta, timezone
def set_token(token, user_id):
    db = get_db()
    try:
        expires_at =datetime.now(timezone.utc) + timedelta(hours=1)
        db.execute("UPDATE usuarios SET reset_token = ?, expires_at = ? WHERE id_usuario = ?", (token, user_id, expires_at))
        db.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def check_token(token):
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE reset_token = ?", (token,)).fetchone()
    if not user:
        db.close()
        return None
    if datetime.now(timezone.utc) > user["expires_at"]:
        # limpiar token expirado
        db.execute("""
            UPDATE usuarios
            SET reset_token = NULL, expires_at = NULL
            WHERE id_usuario = ?
        """, (user["id_usuario"],))
        db.commit()
        db.close()
        return None

    db.close()
    return user


def es_favorita(id_usuario, id_receta):
    db = get_db()
    
    # Buscamos si existe la combinación de usuario y receta
    resultado = db.execute(
        "SELECT 1 FROM preferidas WHERE id_usuario = ? AND id_receta = ?",
        (id_usuario, id_receta)
    ).fetchone()
    
    db.close()
    
    # Si 'resultado' no es None, significa que la encontró
    return resultado is not None

def agregar_favorito(id_usuario, id_receta):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO preferidas (id_usuario, id_receta) VALUES (?, ?)",
            (id_usuario, id_receta)
        )
        db.commit()
    except Exception as e:
        print(f"Error al agregar favorito: {e}")
    finally:
        db.close()

def quitar_favorito(id_usuario, id_receta):
    db = get_db()
    db.execute(
        "DELETE FROM preferidas WHERE id_usuario = ? AND id_receta = ?",
        (id_usuario, id_receta)
    )
    db.commit()
    db.close()

def get_all_recetas(id_usuario):
    db = get_db()
    query = """
        SELECT * FROM recetas 
        WHERE publica = 1 OR id_usuario = ? 
        ORDER BY publica DESC, nombre ASC
    """
    
    rows = db.execute(query, (id_usuario,)).fetchall()
    db.close()
    return rows

def update_menu(id_menu, datos):
    db = get_db()
    try:
        query = """
            UPDATE menu_receta 
            SET id_receta = ?
            WHERE id_menu = ? AND nro_dia = ?
        """

        for item in datos:
            nro_dia = item.get('nro_dia')
            id_receta = item.get('id_receta')
            
            if nro_dia is not None and id_receta:
                db.execute(query, (id_receta, id_menu, nro_dia))

        db.commit()
        return True

    except Exception as e:
        db.rollback()
        print(f"Error actualizando menu_receta: {e}")
        return False
    finally:
        db.close()

def search_recetas(query_texto, comida, tipos, id_usuario, limite, offset):
    db = get_db()
    sql = """
        SELECT DISTINCT r.*,
            (CASE WHEN p.id_receta IS NOT NULL THEN 1 ELSE 0 END) as es_favorita
        FROM recetas r
        LEFT JOIN ingrediente_receta ir ON r.id_receta = ir.id_receta
        LEFT JOIN ingredientes i ON ir.id_ingrediente = i.id_ingrediente
        LEFT JOIN preferidas p ON r.id_receta = p.id_receta AND p.id_usuario = ?
        WHERE (r.publica = 1 OR r.id_usuario = ?)
    """
    params = [id_usuario, id_usuario]

    if query_texto:
        sql += """ AND (r.nombre LIKE ? COLLATE NOCASE 
                     OR r.instrucciones LIKE ? COLLATE NOCASE 
                     OR i.nombre LIKE ? COLLATE NOCASE)"""
        termino = f"{query_texto}"
        params.extend([termino, termino, termino])
    if comida and comida not in ['todas', 'menu', 'None', '']:
        sql += " AND r.comida = ?"
        params.append(comida)
    if tipos:
        # Creamos una lista de '?' según cuántos tipos hayan elegido
        # Ejemplo: AND tipo IN (?, ?)
        placeholders = ', '.join(['?'] * len(tipos))
        sql += f" AND r.tipo IN ({placeholders})"
        params.extend(tipos)

    # 5. Orden: Primero las del usuario, luego el resto por nombre
    sql += " ORDER BY (r.id_usuario = ?) DESC, r.nombre ASC"
    params.append(id_usuario)
    sql += " LIMIT ? OFFSET ?"
    params.append(limite)
    params.append(offset)
    try:
        rows = db.execute(sql, params).fetchall()
        return rows
    except Exception as e:
        print(f"Error en búsqueda: {e}")
        return []
    finally:
        db.close()