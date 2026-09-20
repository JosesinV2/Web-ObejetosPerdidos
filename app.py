from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import json
import re
import os
import uuid
from datetime import datetime, date, timedelta


# =========================================================
# CONFIGURACIÓN DE FLASK
# =========================================================

app = Flask(__name__)

# Clave utilizada por Flask para manejar las sesiones.
# Más adelante podremos cambiarla por una más segura.
app.secret_key = "clave-proyecto-objetos-perdidos"

# @app.before_request
# def revisar_objetos_vencidos():
#     eliminar_objetos_vencidos()


# =========================================================
# RUTAS DE LOS ARCHIVOS JSON
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")

OBJETOS_FILE = os.path.join(DATA_DIR, "objetos.json")
SOLICITUDES_FILE = os.path.join(DATA_DIR, "solicitudes.json")
USUARIOS_FILE = os.path.join(DATA_DIR, "usuarios.json")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def archivo_permitido(nombre):
    return (
        "." in nombre
        and nombre.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# =========================================================
# FUNCIONES PARA TRABAJAR CON JSON
# =========================================================

def cargar_json(ruta):
    """
    Lee un archivo JSON y devuelve su contenido.
    """

    try:

        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    except (FileNotFoundError, json.JSONDecodeError):

        return []


def guardar_json(ruta, datos):
    """
    Guarda información en un archivo JSON.
    """

    with open(ruta, "w", encoding="utf-8") as archivo:

        json.dump(
            datos,
            archivo,
            ensure_ascii=False,
            indent=4
        )


# =========================================================
# FUNCIONES PARA OBJETOS
# =========================================================

def cargar_objetos():
    return cargar_json(OBJETOS_FILE)


def guardar_objetos(objetos):
    guardar_json(OBJETOS_FILE, objetos)

def eliminar_objetos_vencidos():

    objetos = cargar_objetos()

    objetos_actualizados = []

    hoy = date.today()

    for objeto in objetos:

        if objeto.get("estado") == "Entregado":

            fecha_entrega = objeto.get("fecha_entrega", "")

            if fecha_entrega:

                try:
                    fecha = datetime.strptime(
                        fecha_entrega,
                        "%Y-%m-%d"
                    ).date()

                    dias_transcurridos = (hoy - fecha).days

                    if dias_transcurridos >= 14:
                        continue

                except ValueError:
                    pass

        objetos_actualizados.append(objeto)

    guardar_objetos(objetos_actualizados)


# =========================================================
# FUNCIONES PARA SOLICITUDES
# =========================================================

def cargar_solicitudes():
    return cargar_json(SOLICITUDES_FILE)


def guardar_solicitudes(solicitudes):
    guardar_json(SOLICITUDES_FILE, solicitudes)


# =========================================================
# FUNCIONES PARA USUARIOS
# =========================================================

def cargar_usuarios():
    return cargar_json(USUARIOS_FILE)


# =========================================================
# GENERACIÓN DE IDs
# =========================================================

def obtener_siguiente_id(objetos):

    ids = sorted(
        objeto["id"]
        for objeto in objetos
        if isinstance(objeto.get("id"), int)
    )

    siguiente_id = 1

    for id_actual in ids:

        if id_actual == siguiente_id:
            siguiente_id += 1

        elif id_actual > siguiente_id:
            break

    return siguiente_id


# =========================================================
# PROTECCIÓN DEL PANEL ADMINISTRATIVO
# =========================================================

def usuario_autenticado():

    return session.get("usuario") is not None


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.route("/")
def inicio():

    return render_template("index.html")


# =========================================================
# BÚSQUEDA DE OBJETOS
# =========================================================

@app.route("/buscar")
def buscar():

    objetos = cargar_objetos()

    fecha = request.args.get("fecha", "").strip()
    categoria = request.args.get("categoria", "").strip()
    lugar = request.args.get("lugar", "").strip()

    resultados = []

    for objeto in objetos:

        # No mostramos objetos entregados
        if objeto.get("estado") == "Entregado":
            continue

        # Filtro por fecha
        if fecha and objeto.get("fecha") != fecha:
            continue

        # Filtro por categoría
        if categoria and objeto.get("categoria") != categoria:
            continue

        # Filtro por lugar
        if lugar and objeto.get("lugar") != lugar:
            continue

        resultados.append(objeto)

    return render_template(
        "resultados.html",
        objetos=resultados,
        fecha=fecha,
        categoria=categoria,
        lugar=lugar
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None


    if request.method == "POST":

        usuario = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "").strip()


        usuarios = cargar_usuarios()


        acceso_correcto = False


        for cuenta in usuarios:

            if (
                cuenta.get("usuario") == usuario
                and
                cuenta.get("contrasena") == contrasena
            ):

                acceso_correcto = True

                break


        if acceso_correcto:

            session["usuario"] = usuario

            return redirect(url_for("admin"))


        error = "Usuario o contraseña incorrectos."


    return render_template(
        "login.html",
        error=error
    )


# =========================================================
# CERRAR SESIÓN
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("inicio"))


# =========================================================
# PANEL ADMINISTRATIVO
# =========================================================

@app.route("/admin")
def admin():

    if not usuario_autenticado():

        return redirect(url_for("login"))


    objetos = cargar_objetos()

    solicitudes = cargar_solicitudes()


    total = len(objetos)

    disponibles = sum(
        1 for objeto in objetos
        if objeto.get("estado") == "Disponible"
    )

    solicitados = sum(
        1 for objeto in objetos
        if objeto.get("estado") == "Solicitado"
    )

    entregados = sum(
        1 for objeto in objetos
        if objeto.get("estado") == "Entregado"
    )


    solicitudes_pendientes = sum(
        1 for solicitud in solicitudes
        if solicitud.get("estado") == "Pendiente"
    )


    return render_template(
        "admin.html",
        objetos=objetos,
        solicitudes=solicitudes,
        total=total,
        disponibles=disponibles,
        solicitados=solicitados,
        entregados=entregados,
        solicitudes_pendientes=solicitudes_pendientes
    )


# =========================================================
# REGISTRAR OBJETO
# =========================================================    


# =========================================================
# EDITAR OBJETO
# =========================================================



@app.route("/registrar", methods=["GET", "POST"])
def registrar():

    if not usuario_autenticado():
        return redirect(url_for("login"))

    if request.method == "POST":

        objetos = cargar_objetos()

        nombre = request.form.get("nombre", "").strip()
        categoria = request.form.get("categoria", "").strip()
        fecha = request.form.get("fecha", "").strip()
        hora = request.form.get("hora", "").strip()
        lugar = request.form.get("lugar", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if not nombre or not categoria or not fecha or not hora or not lugar or not descripcion:
            return render_template(
                "registrar.html",
                error="Todos los campos obligatorios deben estar completos."
        )

        try:
            fecha_objeto = datetime.strptime(
                fecha,
                "%Y-%m-%d"
            ).date()

            datetime.strptime(
                hora,
                "%H:%M"
            )

        except ValueError:
         return render_template(
            "registrar.html",
            error="La fecha o la hora no tienen un formato válido."
        )
        if fecha_objeto > date.today():
            return render_template(
            "registrar.html",
            error="La fecha de hallazgo no puede ser futura."
        )


    imagen = request.files.get("imagen")
    nombre_imagen = ""

    if imagen and imagen.filename:

        if not archivo_permitido(imagen.filename):
            return render_template(
                "registrar.html",
                error="El archivo seleccionado no es una imagen válida. Usa JPG, PNG o WEBP."
            )

        nombre_seguro = secure_filename(imagen.filename)
        nombre_unico = f"{uuid.uuid4().hex}_{nombre_seguro}"

        ruta_imagen = os.path.join(
            UPLOAD_FOLDER,
            nombre_unico
        )

        imagen.save(ruta_imagen)
        nombre_imagen = f"uploads/{nombre_unico}"

        nuevo_objeto = {

            "id": obtener_siguiente_id(objetos),

            "nombre":
                request.form.get("nombre", "").strip(),

            "categoria":
                request.form.get("categoria", "").strip(),

            "fecha":
                request.form.get("fecha", "").strip(),

            "hora":
                request.form.get("hora", "").strip(),

            "lugar":
                request.form.get("lugar", "").strip(),

            "descripcion":
                request.form.get("descripcion", "").strip(),

            "imagen": nombre_imagen,

            "estado":
                request.form.get(
                    "estado",
                    "Disponible"
                ).strip(),

            "fecha_entrega": ""
        }

        objetos.append(nuevo_objeto)

        guardar_objetos(objetos)

        return redirect(url_for("admin"))

    return render_template("registrar.html")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    if not usuario_autenticado():
        return redirect(url_for("login"))

    objetos = cargar_objetos()

    objeto = next(
        (objeto for objeto in objetos if objeto["id"] == id),
        None
    )

    if objeto is None:
        return redirect(url_for("admin"))

    if request.method == "POST":



        objeto["nombre"] = request.form.get(
            "nombre",
            ""
        ).strip()

    objeto["categoria"] = request.form.get(
            "categoria",
            ""
        ).strip()

    objeto["fecha"] = request.form.get(
            "fecha",
            ""
        ).strip()

    objeto["hora"] = request.form.get(
            "hora",
            ""
        ).strip()

    objeto["lugar"] = request.form.get(
            "lugar",
            ""
        ).strip()

    objeto["descripcion"] = request.form.get(
            "descripcion",
            ""
        ).strip()


    nuevo_estado = request.form.get(
            "estado",
            objeto.get("estado")
        ).strip()


        # Si cambia a Entregado,
        # registramos la fecha automáticamente.
    if (
            nuevo_estado == "Entregado"
            and objeto.get("estado") != "Entregado"
        ):

            objeto["fecha_entrega"] = date.today().isoformat()


        # Si deja de estar Entregado,
        # eliminamos la fecha de entrega.
    elif nuevo_estado != "Entregado":

            objeto["fecha_entrega"] = ""


    objeto["estado"] = nuevo_estado


    guardar_objetos(objetos)


    return redirect(url_for("admin"))


    return render_template(
        "editar.html",
        objeto=objeto
    )


# =========================================================
# ELIMINAR OBJETO
# =========================================================

@app.route("/eliminar/<int:id>")
def eliminar(id):

    if not usuario_autenticado():

        return redirect(url_for("login"))


    objetos = cargar_objetos()


    objetos = [
        objeto
        for objeto in objetos
        if objeto.get("id") != id
    ]


    guardar_objetos(objetos)


    return redirect(url_for("admin"))


# =========================================================
# SOLICITUD DE RECUPERACIÓN
# =========================================================

@app.route("/solicitar/<int:id>", methods=["GET", "POST"])
def solicitar(id):

    objetos = cargar_objetos()

    objeto = None

    for objeto_actual in objetos:

        if objeto_actual.get("id") == id:

            objeto = objeto_actual

            break

    if objeto is None:

        return redirect(url_for("buscar"))

    # No permitir solicitudes sobre objetos
    # que ya no están disponibles.
    if objeto.get("estado") != "Disponible":

        return redirect(url_for("buscar"))

    if request.method == "POST":

        nombre = request.form.get(
            "nombre",
            ""
        ).strip()

        cif = request.form.get(
            "cif",
            ""
        ).strip()

        correo = request.form.get(
            "correo",
            ""
        ).strip()

        telefono = request.form.get(
            "telefono",
            ""
        ).strip()

        fecha_recogida = request.form.get(
            "fecha_recogida",
            ""
        ).strip()

        hora_recogida = request.form.get(
            "hora_recogida",
            ""
        ).strip()

        error_cif = ""

        error_telefono = ""

        error_correo = ""

        # Validar CIF
        if (
            len(cif) != 8
            or not cif.isascii()
            or not cif.isdigit()
        ):

            error_cif = (
                "El CIF debe tener exactamente 8 números."
            )

        # Validar teléfono
        if (
            len(telefono) != 8
            or not telefono.isascii()
            or not telefono.isdigit()
        ):

        # Validar correo
            if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
    correo
):

                error_correo = (
        "Ingresa un correo electrónico válido."
    )

            error_telefono = (
                "El teléfono debe tener exactamente 8 números."
            )

        # Si existe algún error, volver al formulario
        if error_cif or error_telefono or error_correo:

            return render_template(
                "solicitud.html",
                objeto=objeto,
                error_cif=error_cif,
                error_telefono=error_telefono,
                error_correo=error_correo
            )

        solicitudes = cargar_solicitudes()

        nueva_solicitud = {

            "id": (
                max(
                    [
                        solicitud.get("id", 0)
                        for solicitud in solicitudes
                    ],
                    default=0
                ) + 1
            ),

            "objeto_id": id,

            "nombre": nombre,

            "cif": cif,

            "correo": correo,

            "telefono": telefono,

            "fecha_recogida": fecha_recogida,

            "hora_recogida": hora_recogida,

            "estado": "Pendiente",

            "fecha_solicitud":
                date.today().isoformat()

        }

        solicitudes.append(nueva_solicitud)

        guardar_solicitudes(solicitudes)

        # Cambiamos automáticamente
        # el objeto a Solicitado.
        objeto["estado"] = "Solicitado"

        guardar_objetos(objetos)

        return redirect(url_for("buscar"))

    return render_template(
        "solicitud.html",
        objeto=objeto
    )

# EJECUCIÓN DEL SERVIDOR

if __name__ == "__main__":

    app.run(
        debug=True
    )