from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from functools import wraps
import requests
import os

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def apology(mensaje, codigo=400):
    return render_template("apology.html", mensaje=mensaje, codigo=codigo), codigo

def enviar_mail(destinatario, link):
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        print("ERROR: No se encontró la API KEY en las variables de entorno")
        return 500
    
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "onboarding@resend.dev",
                "to": destinatario,
                "subject": "Recuperar contraseña",
                "html": f"""
                    <p>Hacé click para cambiar tu contraseña:</p>
                    <a href="{link}">Resetear contraseña</a>
                """
            }
        )
        print("Código:", response.status_code)
        print("Respuesta:", response.text)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error enviando mail: {e}")
        return None