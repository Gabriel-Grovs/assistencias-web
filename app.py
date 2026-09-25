"""Aplicação Flask — Sistema de Assistências.

- Login por senha via sessão (``APP_PASSWORD``).
- Rota ``/`` (protegida) com a tela principal.
- Rota ``/processar`` (protegida) que extrai os dados e grava no Google Sheets.
"""

import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from extractor.extractor import extract_record
from sheets.writer import append_row

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["SESSION_PERMANENT"] = False

APP_PASSWORD = os.environ.get("APP_PASSWORD") or "123gabriel"


def login_required(view):
    """Protege rotas: redireciona para /login se não autenticado."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        if APP_PASSWORD and password == APP_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        error = "Senha incorreta"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/planilha")
def planilha():
    sheet_id = os.environ.get("GOOGLE_SHEET_ID") or "1OMof37tDGTYj0JKV2A34QN42OB49en6B0Ro1w5tDwl8"
    return redirect(f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit?usp=sharing", code=302)


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/processar", methods=["POST"])
@login_required
def processar():
    text = request.form.get("texto", "")
    if not text.strip():
        return jsonify({"ok": False, "erro": "Texto vazio"}), 400

    record = extract_record(text)

    sheet_result = append_row(record)

    return jsonify({"ok": True, "registro": record, "sheets": sheet_result})
