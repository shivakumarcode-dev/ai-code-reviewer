import os
import json
import sqlite3
from functools import wraps
from pathlib import Path

import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "codereview.db"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-local-development-secret")


def db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            language TEXT NOT NULL,
            code TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")


init_db()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Please log in first."}), 401
        return fn(*args, **kwargs)
    return wrapper


def ask_ollama(prompt, system=None):
    """Send a prompt to the locally running Ollama server."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.2}
            },
            timeout=180
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Ollama is not running. Open Ollama, then try again.")
    except requests.exceptions.Timeout:
        raise RuntimeError("The model took too long to respond. Try a smaller model or shorter code.")
    except requests.exceptions.HTTPError as exc:
        detail = ""
        try:
            detail = response.json().get("error", "")
        except Exception:
            pass
        if response.status_code == 404:
            raise RuntimeError(f"Model '{OLLAMA_MODEL}' was not found. Run: ollama pull {OLLAMA_MODEL}")
        raise RuntimeError(detail or f"Ollama returned HTTP {response.status_code}.") from exc


@app.get("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth"))
    return render_template("index.html", username=session.get("username"), model=OLLAMA_MODEL)


@app.route("/auth", methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        action = request.form.get("action")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Enter both username and password.", "error")
            return redirect(url_for("auth"))
        with db() as conn:
            if action == "register":
                try:
                    cur = conn.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (username, generate_password_hash(password))
                    )
                    session["user_id"] = cur.lastrowid
                    session["username"] = username
                    return redirect(url_for("index"))
                except sqlite3.IntegrityError:
                    flash("That username is already taken.", "error")
            else:
                user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
                if user and check_password_hash(user["password_hash"], password):
                    session["user_id"] = user["id"]
                    session["username"] = user["username"]
                    return redirect(url_for("index"))
                flash("Incorrect username or password.", "error")
    return render_template("auth.html")


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth"))


@app.get("/api/health")
def health():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=4)
        r.raise_for_status()
        models = [m.get("name") for m in r.json().get("models", [])]
        return jsonify({"ollama": "connected", "model": OLLAMA_MODEL, "model_available": any(
            name == OLLAMA_MODEL or name.startswith(OLLAMA_MODEL.split(":")[0] + ":") for name in models
        ), "models": models})
    except Exception:
        return jsonify({"ollama": "offline", "model": OLLAMA_MODEL, "model_available": False}), 503


@app.post("/api/review")
@login_required
def review():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "").strip()
    language = data.get("language", "Python")
    if not code:
        return jsonify({"error": "Paste some code before starting a review."}), 400
    if len(code) > 20000:
        return jsonify({"error": "Please keep the code under 20,000 characters."}), 400

    system = """You are a careful senior software engineer reviewing code for a beginner developer.
Return valid JSON only, with this exact structure:
{
 "summary": "short overall assessment",
 "issues": [{"severity":"High|Medium|Low","line":1,"title":"...","explanation":"...","suggestion":"..."}],
 "strengths": ["..."],
 "improved_code": "optional corrected code or empty string"
}
Do not invent line numbers; use null if uncertain. Be specific, kind, and educational.
If there are no issues, return an empty issues array."""
    prompt = f"Review this {language} code. Identify bugs, readability issues, and improvements. Explain simply.\n\nCODE:\n```{language}\n{code}\n```"
    try:
        raw = ask_ollama(prompt, system)
        parsed = extract_json(raw)
        result_text = json.dumps(parsed, ensure_ascii=False)
        with db() as conn:
            conn.execute(
                "INSERT INTO reviews (user_id, language, code, result) VALUES (?, ?, ?, ?)",
                (session["user_id"], language, code, result_text)
            )
        return jsonify(parsed)
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        return jsonify({"error": str(exc)}), 503


@app.post("/api/fix")
@login_required
def fix_code():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "").strip()
    language = data.get("language", "Python")
    if not code:
        return jsonify({"error": "Paste code first."}), 400
    try:
        answer = ask_ollama(
            f"Find and fix bugs in this {language} code. Return only the complete corrected code, without markdown fences. Preserve the original intent.\n\n{code}",
            "You are an expert programming assistant. Return code only."
        )
        return jsonify({"code": strip_fences(answer)})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503


@app.post("/api/convert")
@login_required
def convert_code():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "").strip()
    source = data.get("source", "Python")
    target = data.get("target", "Java")
    if not code:
        return jsonify({"error": "Paste code first."}), 400
    try:
        answer = ask_ollama(
            f"Convert this code from {source} to {target}. Keep the same behavior. Return complete code only, without markdown fences.\n\n{code}",
            "You are an expert polyglot programmer. Return code only."
        )
        return jsonify({"code": strip_fences(answer)})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503


@app.get("/api/history")
@login_required
def history():
    with db() as conn:
        rows = conn.execute(
            "SELECT id, language, substr(code,1,100) AS preview, created_at FROM reviews WHERE user_id=? ORDER BY id DESC LIMIT 20",
            (session["user_id"],)
        ).fetchall()
    return jsonify([dict(row) for row in rows])


def strip_fences(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2 and lines[-1].strip().startswith("```"):
            return "\n".join(lines[1:-1]).strip()
    return text


def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = strip_fences(text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("The model did not return valid review data. Try again.")
    return json.loads(text[start:end + 1])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
