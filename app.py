from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
import json

app = Flask(__name__)

ARCHIVO = Path(__file__).resolve().parent / "usuarios.json"


def cargar_usuarios():
    if not ARCHIVO.exists():
        return []

    with open(ARCHIVO, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_usuarios(usuarios):
    with open(ARCHIVO, "w", encoding="utf-8") as archivo:
        json.dump(usuarios, archivo, indent=4, ensure_ascii=False)


@app.route("/")
def inicio():
    return jsonify({
        "mensaje": "Servidor MiAgenda funcionando"
    })


@app.route("/registro", methods=["POST"])
def registrar_usuario():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "mensaje": "Se requiere un JSON válido"
        }), 400

    campos = ["nombre", "correo", "rut", "login", "password"]

    if any(
        not isinstance(datos.get(campo), str)
        or not datos[campo].strip()
        for campo in campos
    ):
        return jsonify({
            "mensaje": "Todos los campos son obligatorios"
        }), 400

    usuarios = cargar_usuarios()

    if any(u["login"] == datos["login"] for u in usuarios):
        return jsonify({
            "mensaje": "El nombre de usuario ya existe"
        }), 409

    nuevo_usuario = {
        "nombre": datos["nombre"],
        "correo": datos["correo"],
        "rut": datos["rut"],
        "login": datos["login"],
        "password_hash": generate_password_hash(datos["password"])
    }

    usuarios.append(nuevo_usuario)
    guardar_usuarios(usuarios)

    return jsonify({
        "mensaje": "Usuario registrado correctamente"
    }), 201


@app.route("/login", methods=["POST"])
def login():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "valido": False,
            "mensaje": "Se requiere un JSON válido"
        }), 400

    nombre_usuario = datos.get("login")
    password = datos.get("password")

    if not isinstance(nombre_usuario, str) or not isinstance(password, str):
        return jsonify({
            "valido": False,
            "mensaje": "Credenciales inválidas"
        }), 400

    usuarios = cargar_usuarios()

    for usuario in usuarios:
        if (
            usuario["login"] == nombre_usuario
            and check_password_hash(usuario["password_hash"], password)
        ):
            return jsonify({
                "valido": True,
                "mensaje": "Inicio de sesión exitoso"
            }), 200

    return jsonify({
        "valido": False,
        "mensaje": "Credenciales incorrectas"
    }), 401


@app.route("/usuario", methods=["GET"])
def obtener_usuario():
    usuarios = cargar_usuarios()

    if not usuarios:
        return jsonify({
            "mensaje": "No hay usuarios registrados"
        }), 404

    usuario = usuarios[-1]

    return jsonify({
        "nombre": usuario["nombre"],
        "correo": usuario["correo"],
        "rut": usuario["rut"]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
