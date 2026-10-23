"""Aplicação Flask — Sistema de Assistências.

- Login protegido com rate-limiting, timing-attack protection e anti-injection.
- Headers HTTP de segurança (CSP, X-Frame-Options, X-Content-Type-Options).
- Rota ``/`` (protegida) com a tela principal.
- Rota ``/processar`` (protegida) que extrai os dados e grava no Google Sheets.
"""

from collections import defaultdict
from functools import wraps
import hmac
import logging
import os
import re
import time

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from extractor.extractor import extract_record
from sheets.writer import append_row

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["SESSION_PERMANENT"] = False

# Hardening de cookies de sessão
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.environ.get("RENDER") is not None
    or os.environ.get("FLASK_ENV") == "production"
)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # Limite de 2MB para payload

APP_PASSWORD = os.environ.get("APP_PASSWORD") or "123gabriel"

# Rate limiting em memória para proteção contra força bruta
# Armazena lista de timestamps de falhas por IP
_LOGIN_FAILURES = defaultdict(list)
_MAX_FAILURES = 5
_LOCKOUT_TIME = 900  # 15 minutos em segundos

# Padrões suspeitos para sanitização contra SQL Injection e ataques web na tela de login
_SQLI_PATTERN = re.compile(
    r"(\b(UNION(\s+ALL)?\s+SELECT|SELECT\s+.*?\s+FROM|INSERT\s+INTO|DROP\s+(TABLE|DATABASE)|UPDATE\s+.*?\s+SET|DELETE\s+FROM)\b|"
    r"'\s*OR\s*['\"\d]|--|/\*|\*/|;\s*SHUTDOWN|EXEC(\s|\+)+(SP_|XP_))",
    re.IGNORECASE,
)


def _get_client_ip():
    """Identifica o IP real do cliente, considerando proxies reversos (Render)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def _is_rate_limited(ip):
    """Verifica se o IP excedeu o número máximo de tentativas nas últimas janelas de tempo."""
    now = time.time()
    # Remove timestamps mais antigos que _LOCKOUT_TIME
    _LOGIN_FAILURES[ip] = [t for t in _LOGIN_FAILURES[ip] if now - t < _LOCKOUT_TIME]
    return len(_LOGIN_FAILURES[ip]) >= _MAX_FAILURES


def _record_failure(ip):
    """Registra uma falha de autenticação para o IP."""
    _LOGIN_FAILURES[ip].append(time.time())


def _clear_failures(ip):
    """Limpa o histórico de falhas do IP após sucesso."""
    if ip in _LOGIN_FAILURES:
        del _LOGIN_FAILURES[ip]


@app.after_request
def apply_security_headers(response):
    """Aplica cabeçalhos HTTP de segurança estritos em todas as respostas."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "script-src 'self' 'unsafe-inline';"
    )
    return response


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
    ip = _get_client_ip()

    if request.method == "POST":
        # 1. Checagem de Rate-Limiting contra Força Bruta
        if _is_rate_limited(ip):
            logger.warning("Bloqueio de força bruta ativo para o IP %s", ip)
            error = "Muitas tentativas incorretas. Acesso bloqueado temporariamente por 15 minutos."
            return render_template("login.html", error=error), 429

        password = request.form.get("password", "")

        # 2. Sanitização estrita e proteção contra SQL Injection / Null Bytes / Payload Overflow
        if not isinstance(password, str) or "\x00" in password or len(password) > 128:
            _record_failure(ip)
            logger.warning("Tentativa com caracteres ilegais ou tamanho excessivo do IP %s", ip)
            error = "Entrada inválida ou malformada. Acesso rejeitado."
            return render_template("login.html", error=error), 400

        if _SQLI_PATTERN.search(password):
            _record_failure(ip)
            logger.warning("Padrão de SQL Injection detectado no login pelo IP %s", ip)
            error = "Tentativa de injeção maliciosa detectada e neutralizada."
            return render_template("login.html", error=error), 400

        # 3. Comparação segura em tempo constante (Timing Attack Protection)
        if APP_PASSWORD and hmac.compare_digest(password, APP_PASSWORD):
            _clear_failures(ip)
            # Regenera a sessão para evitar Session Fixation
            session.clear()
            session["logged_in"] = True
            logger.info("Login realizado com sucesso pelo IP %s", ip)
            return redirect(url_for("index"))

        # Falha de senha comum
        _record_failure(ip)
        tentativas_restantes = max(0, _MAX_FAILURES - len(_LOGIN_FAILURES[ip]))
        logger.warning(
            "Senha incorreta para o IP %s. Tentativas restantes: %d",
            ip,
            tentativas_restantes,
        )
        if tentativas_restantes > 0:
            error = f"Senha incorreta ({tentativas_restantes} tentativa(s) restante(s))"
        else:
            error = "Muitas tentativas incorretas. Acesso bloqueado temporariamente por 15 minutos."

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
    if not isinstance(text, str) or not text.strip():
        return jsonify({"ok": False, "erro": "Texto vazio"}), 400

    if "\x00" in text:
        return jsonify({"ok": False, "erro": "Conteúdo com caracteres inválidos"}), 400

    try:
        record = extract_record(text)
        sheet_result = append_row(record)
        return jsonify({"ok": True, "registro": record, "sheets": sheet_result})
    except Exception as exc:  # noqa: BLE001
        logger.error("Erro ao processar assistência: %s", exc)
        return jsonify({"ok": False, "erro": "Falha interna ao processar texto"}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=False)
