from flask import render_template, request, redirect, flash, session, url_for, current_app
from flask_session import Session
from app import app
import app.models as models
from app.helpers import login_required, apology, enviar_mail
from werkzeug.security import check_password_hash, generate_password_hash
from secrets import token_urlsafe
from werkzeug.utils import secure_filename
import os

@app.route("/", methods=["GET", "POST"])
def buscar():
    query_texto = request.form.get("query") or request.args.get("query", "")
    comida_input = request.form.get("comida") or request.args.get("comida")
    tipos = request.form.getlist("tipo") or request.args.getlist("tipo")
    accion = request.form.get("accion")

    comida_original = comida_input if comida_input else "todas"
    
    comida_db = 'cena' if comida_input == 'almuerzo' else comida_input
    if not comida_db or comida_db in ["None", "todas", "menu"]:
        comida_db = "todas"

    page = request.args.get('page',1, type=int)
    limite = 12
    offset = (page - 1) * limite
    id_usuario = session.get("user_id")
    if request.method == "POST":
        if accion == "generar":
            menu = models.obtener_menu_aleatorio(tipos)
            if menu is None:
                flash("No se pudo armar el menú con esos filtros")
                return redirect(url_for('buscar'))
            print(menu)
            desayunos, cenas = menu
            if id_usuario is None:
                return redirect(url_for("login", next=request.url))
            models.guardar_menu(desayunos, cenas, id_usuario)
            return redirect("/menu")

    
        resultados = models.search_recetas(query_texto, comida_db, tipos, id_usuario,limite,offset)
        return render_template('index.html', 
                               recetas=resultados, 
                               query=query_texto, 
                               current_comida=comida_original, 
                               tipos_seleccionados=tipos,
                               page=page,
                               hay_mas=len(resultados)==limite)

    resultados = models.search_recetas("", comida_db, tipos, id_usuario, limite, offset)
    return render_template('index.html', 
                           recetas=resultados, 
                           current_comida=comida_original, 
                           tipos_seleccionados=tipos,
                           page=page,
                           hay_mas=len(resultados)==limite)

@app.route("/menu", methods=["GET", "POST"])
@login_required
def menu():
    id_usuario = session.get('user_id')
    
    id_menu = request.args.get("id", type=int)  # devuelve None si no hay

    if id_menu:
        datos = models.obtener_datos_menu(id_usuario, id_menu)
        if not datos:
            flash("No se encontró el menú solicitado.", "warning")
            return redirect("/")
    else:
        datos = models.obtener_datos_menu_usuario(id_usuario)
        if not datos:
            flash("Aún no has creado tu menu semanal", "info")
            return redirect("/")

    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return render_template(
        "menu.html", 
        desayunos=datos['desayunos'], 
        cenas=datos['cenas'], 
        ingredientes=datos['ingredientes'], 
        dias=dias
    )



@app.route("/agregar", methods=["GET", "POST"])
@login_required
def agregar():
    if request.method == "POST":
        # 1. Obtener datos del form
        datos_receta = dict()
        datos_receta["nombre"] = request.form.get("nombre")
        datos_receta["comida"] = request.form.get("comida")
        datos_receta["tiempo"] = request.form.get("tiempo")
        datos_receta["ingredientes"] = request.form.getlist("ingredientes")
        datos_receta["instrucciones"] = request.form.get("instrucciones")
        datos_receta["precio_estimado"] = request.form.get("rango_precio", type=int)
        foto = request.files.get('imagen')
        filename = None
        if foto and foto.filename != '':
            filename = secure_filename(foto.filename)
            filename = f"{session['user_id']}_{filename}" 
            ruta_destino = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            foto.save(ruta_destino)
            print(filename)
        datos_receta["image_ruta"] = filename

        tipos_lista = request.form.getlist("tipo")
        tipos_str = ", ".join(tipos_lista)
        datos_receta["tipo"] = tipos_str
        # 3. Validar campos obligatorios
        if not datos_receta["nombre"] or not datos_receta["comida"]:
            return apology("Nombre y Tipo de comida son obligatorios", 400)

        # 4. Guardar en DB
        datos_receta["publica"] = 1 if request.form.get("publica") else 0
        datos_receta["id_usuario"] = session["user_id"]
        if models.insertar_receta(datos_receta):
            nombre = datos_receta["nombre"]
            flash(f"Receta '{nombre}' agregada con éxito", "success")
            return redirect("/")
        else:
            return apology("Error al guardar la receta en la base de datos", 500)
    return render_template("agregar.html")

@app.route("/editar_receta/<int:id>", methods=["GET", "POST"])
@login_required
def editar_receta(id):
    if request.method == "POST":
        datos_receta = dict()
        datos_receta["id_receta"] = id
        datos_receta["nombre"] = request.form.get("nombre")
        datos_receta["comida"] = request.form.get("comida")
        datos_receta["tiempo"] = request.form.get("tiempo")
        datos_receta["ingredientes"] = request.form.getlist("ingredientes")
        datos_receta["instrucciones"] = request.form.get("instrucciones")
        datos_receta["precio_estimado"] = request.form.get("rango_precio", type=int)
        foto = request.files.get('imagen')
        if foto and foto.filename != '':
            filename = secure_filename(foto.filename)
            filename = f"{session['user_id']}_{filename}" 
            ruta_destino = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            foto.save(ruta_destino)
            datos_receta["image_ruta"] = filename
        else:
            receta_actual, _ = models.get_receta(id)
            datos_receta["image_ruta"] = receta_actual["image_ruta"]
        # 2. Manejar el select multiple (devuelve una lista)
        # Los unimos con comas para guardarlos como un solo texto
        tipos_lista = request.form.getlist("tipo")
        tipos_str = ", ".join(tipos_lista)
        datos_receta["tipo"] = tipos_str
        # 3. Validar campos obligatorios
        if not datos_receta["nombre"] or not datos_receta["comida"]:
            return apology("Nombre y Tipo de comida son obligatorios", 400)

        # 4. Guardar en DB
        datos_receta["publica"] = 1 if request.form.get("publica") else 0
        datos_receta["id_usuario"] = session["user_id"]
        if models.editar_receta(datos_receta):
            flash(f"Receta '{datos_receta['nombre']}' editada con éxito", "success")
            return redirect("/")
        else:
            return apology("Error al guardar la receta en la base de datos", 500)
    receta, ingredientes = models.get_receta(id)
    return render_template("agregar.html", receta=receta, ingredientes=ingredientes)


@app.route("/login", methods=["GET", "POST"])
def login():
    """iniciar sesion"""

    # Forget any user_id
    session.clear()
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        contraseña = request.form.get("contraseña")
        usuario = request.form.get("usuario")
        # Ensure username was submitted
        if not usuario:
            return apology("Debes ingresar un nombre de usuario", 403)

        # Ensure password was submitted
        elif not contraseña:
            return apology("Debes ingresar una contraseña", 403)

        # Query database for username
        usuario_db = models.get_user(usuario)

        
        # Ensure username exists and password is correct
        if usuario_db is None or not check_password_hash(usuario_db["hash"], contraseña):
            return apology("Nombre de usuario o contraseña incorrecta", 403)

        # Remember which user has logged in
        session["user_id"] = usuario_db["id_usuario"]
        flash(f"¡Bienvenido de nuevo, {usuario}!", "success")

        next_page = request.args.get("next")

        if next_page:
            return redirect(next_page)
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/salir")
@login_required
def salir():
    """cerrar sesion"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/perfil")
@login_required
def usuario():
    user_id = session["user_id"]
    usuario = models.get_user_info(user_id)
    menus = models.get_menus(user_id)
    recetas = models.get_recetas_for_user(user_id, True)
    return render_template("usuario.html", usuario=usuario, menus=menus, recetas=recetas)

@app.route("/perfil/menus")
@login_required
def ver_menus():
    user_id = session["user_id"]
    
    menus = models.get_menus(user_id)
    
    # Renderizás un template nuevo o el mismo, pero solo con la data de menús
    return render_template("tusmenus.html", menus=menus)

@app.route("/perfil/recetas")
@app.route("/perfil/recetas/<int:otro_user_id>")
def ver_recetas(otro_user_id=None):
    user_id = session.get("user_id")
    target_id = otro_user_id if otro_user_id is not None else user_id
    propia = (target_id==user_id)
    recetas = models.get_recetas_for_user(target_id, propia)
    recetas_favoritas = None
    if propia:
        recetas_favoritas = models.get_recetas_favoritas(user_id)
    nombre = models.get_user_info(target_id)['nombre']
    return render_template("tusrecetas.html", 
                           recetas=recetas, 
                           recetas_favoritas=recetas_favoritas,
                           propia=propia,
                           nombre=nombre)

@app.route("/cambiar_contraseña", methods=["GET", "POST"])
@login_required
def cambiar_contraseña():
    if request.method == "POST":
        user_id = session["user_id"]

        actual = request.form.get("actual")
        nueva = request.form.get("nueva")
        confirmar = request.form.get("confirmar")

        if not actual or not nueva or not confirmar:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("cambiar_contraseña.html")
        
        if nueva != confirmar:
            flash("La nueva contraseña y su confirmación no coinciden.", "danger")
            return render_template("cambiar_contraseña.html")

        user_db = models.get_user_info(user_id)
        if not check_password_hash(user_db["hash"], actual):
            flash("La contraseña actual es incorrecta.", "danger")
            return render_template("cambiar_contraseña.html")
        
        new_hash = generate_password_hash(nueva)
        if not models.actualizar_contraseña(user_id, new_hash):
            flash("Error al actualizar la contraseña", "danger")
            return render_template("cambiar_contraseña")
        flash("Constraseña actualizada correctamente.", "success")
        return redirect("/perfil")
    return render_template("cambiar_contraseña.html")

@app.route("/registrarse", methods=["GET", "POST"])
def registrarse():
    # forget any user id
    session.clear()

    if request.method == "POST":
        usuario = request.form.get("usuario")
        contraseña = request.form.get("contraseña")
        mail = request.form.get("mail")
        # Ensure username was submitted
        if not usuario:
            return apology("Debe ingresar un usuario", 400)

        # Ensure password was submitted
        elif not contraseña:
            return apology("Debe ingresar un contraseña", 400)

        # Ensure confirm password is correct
        elif request.form.get("confirmacion") != contraseña:
            return apology("Las contraseñas no coinciden", 400)
        
        # Query database for username
        if models.get_user(usuario) is not None:
            return apology("El nombre de usuario no está disponible")
        if models.check_mail(mail) is not None:
            return apology("El correo electrónico ya está registrado")
        nuevo_id = models.insert_user(usuario, generate_password_hash(contraseña), mail)
        if nuevo_id:
            flash("Se registró correctamente!", "success")
            session["user_id"] = nuevo_id
            return redirect("/")
        return apology("Error al crear la cuenta", 500)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("registrarse.html")
    

@app.route("/receta/<int:id>")
def receta(id):
    receta, ingredientes = models.get_receta(id)
    if receta is None:
        return apology("Receta no encontrada", 404)
    
    user_id = session.get("user_id")
    es_dueño = (user_id == receta['id_usuario'])
    if not receta['publica'] and not es_dueño:
        return apology("Receta no encontrada", 403)
    es_favorita = False
    if user_id: es_favorita = models.es_favorita(session['user_id'], id)
    dueño = models.get_user_info(receta['id_usuario'])
    return render_template("receta.html", 
                           receta=receta, 
                           ingredientes=ingredientes, 
                           es_favorita=es_favorita,
                           dueño=dueño,
                           )

@app.route("/eliminar_menu", methods=["POST"])
@login_required
def eliminar_menu():
    id_menu = request.form.get("id_menu")
    id_usuario = session["user_id"]
    if not models.delete_menu(id_menu, id_usuario):
        flash("Error al eliminar el menú", "warning")
        return redirect("/perfil")

    flash("Menú eliminado correctamente", "success")
    return redirect("/perfil")

@app.route("/eliminar_receta", methods=["POST"])
@login_required
def eliminar_receta():
    id_receta = request.form.get("id_receta")
    id_usuario = session["user_id"]

    if not models.delete_receta(id_receta, id_usuario):
        flash("Error al eliminar la receta", "warning")
        return redirect("/perfil")

    flash("Receta eliminada correctamente", "success")
    return redirect("/perfil")

@app.route("/olvide_contraseña", methods=["POST", "GET"])
def olvide_contraseña():
    if request.method == "POST":
        user = request.form.get("user")
        mail = request.form.get("mail")

        user_db = models.get_user(user)

        if not user_db:
            user_db = models.check_mail(mail)
            if not user_db:
                flash("No encontramos un usuario con esos datos", "warning")
                return redirect("/")
        
        token = token_urlsafe(32)

        models.set_token(token, user_db["id_usuario"])

        link = url_for("resetear_contraseña", token=token, _external=True)
        # 📧 por ahora simulamos el mail
        enviar_mail(user_db["mail"], link)

        flash("Te enviamos un link para recuperar tu contraseña", "info")
        return redirect("/login")

        redirect("/login")
    return render_template("olvide_contraseña.html")


@app.route("/resetear/<token>", methods=["GET", "POST"])
def resetear_contraseña(token):
    usuario = models.check_token(token)

    if not usuario:
        flash("Token inválido o expirado", "danger")
        return redirect("/login")

    if request.method == "POST":
        nueva = request.form.get("nueva")
        confirmacion = request.form.get("confirmacion")

        if nueva != confirmacion:
            flash("Las contraseñas no coinciden", "warning")
            return redirect(request.url)

        hash_pw = generate_password_hash(nueva)

        if models.actualizar_contraseña(usuario["id_usuario"], hash_pw):
            flash("Contraseña actualizada", "success")
            return redirect("/login")
        flash("No se pudo actualizar su contraseña", "warning")
        return redirect("/login")
    return render_template("resetear.html", token=token)


@app.route("/marcar_favorita", methods=["POST"])
@login_required
def marcar_favorita():
    id_usuario = session["user_id"]
    id_receta = request.form.get("id_receta")

    if not id_receta:
        return apology("Receta no encontrada", 400)

    # 1. Verificamos si ya es favorita
    ya_es = models.es_favorita(id_usuario, id_receta)

    if ya_es:
        # 2. Si ya es, la quitamos (Toggle OFF)
        models.quitar_favorito(id_usuario, id_receta)
        flash("Quitada de tus favoritas")
    else:
        # 3. Si no es, la agregamos (Toggle ON)
        models.agregar_favorito(id_usuario, id_receta)
        flash("¡Guardada en tus favoritas! ⭐")

    # Redirigimos de vuelta a la receta para ver el cambio en el botón
    return redirect(url_for('receta', id=id_receta))

@app.route('/editar-menu/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_menu(id):
    if request.method == 'POST':
        # 1. Creamos la lista de diccionarios que espera tu función update_menu
        datos_para_db = []
        
        for key, value in request.form.items():
            if key.startswith('slot_'):
                # Extraemos el número del nombre del input (ej: 'slot_9' -> 9)
                nro_slot = int(key.split('_')[1])
                id_receta = int(value)
                
                datos_para_db.append({
                    'nro_dia': nro_slot,
                    'id_receta': id_receta
                })
        
        # 2. Llamamos a la función que armamos antes
        if models.update_menu(id, datos_para_db):
            flash("Menú actualizado con éxito", "success")
            return redirect(url_for('ver_menus'))
        else:
            flash("Error al actualizar", "danger")

    # GET: Mantener igual, pero asegurate de que menu_actual tenga los nro_dia
    id_usuario = session["user_id"]
    menu_actual = models.obtener_datos_menu(id_usuario, id)
    recetas = models.get_all_recetas(id_usuario)
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return render_template('editar_menu.html', menu=menu_actual, recetas=recetas, dias=dias)