from flask import Flask, jsonify, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

import sqlite3

from helpers import login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_db():
    conn = sqlite3.connect("typeIT50.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return render_template("register.html", error="Username is required.")
        if not password:
            return render_template("register.html", error="Password is required.")
        if password != confirmation:
            return render_template("register.html", error="Passwords do not match.")

        conn = get_db()
        cursor = conn.cursor()

        user_exists = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user_exists:
            return render_template("register.html", error="Username already exists.")

        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()

        return render_template("login.html", message="Registration successful. Please log in.")

    return render_template("register.html")


@app.route("/login", methods = ["GET", "POST"])
def login():

    session.clear()
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template("login.html", error="Username is required.")
        if not password:
            return render_template("login.html", error="Password is required.")

        conn = get_db()
        cursor = conn.cursor()

        user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["hash"], password):
            return render_template("login.html", error="Invalid username or password.")

        session["user_id"] = user["id"]
        return render_template("index.html", username=username)

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html")

@app.route("/api/words")
@login_required
def get_words():
    count = request.args.get("count", default=100, type=int)

    db = get_db()
    cursor = db.cursor()
    rows = cursor.execute("SELECT word FROM words ORDER BY RANDOM() LIMIT ?", (count,)).fetchall()
    db.close()

    stream = [row["word"] for row in rows]

    return jsonify({"words": stream})


@app.route("/api/submit_race", methods = ["POST"])
@login_required
def submit_race():
    data = request.get_json()

    duration_mode = data.get("duration_mode")
    correct_chars = data.get("correct_chars")
    total_chars_typed = data.get("total_chars_typed")

    if duration_mode not in (15, 30, 60):
        return jsonify({"error": "Invalid duration mode."}), 400
    if correct_chars is None or total_chars_typed is None:
        return jsonify({"error": "Missing required data."}), 400

    minutes = duration_mode / 60
    wpm = round((correct_chars / 5) / minutes, 2)
    accuracy = round((correct_chars / total_chars_typed) * 100, 2) if total_chars_typed > 0 else 0.00

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO races (user_id, duration_mode, wpm, accuracy, correct_chars) VALUES (?, ?, ?, ?, ?)",
        (session["user_id"], duration_mode, wpm, accuracy, correct_chars)
    )

    db.commit()
    db.close()

    return jsonify({"wpm": wpm, "accuracy": accuracy})


@app.route("/leaderboard")
def leaderboard():
    duration_mode = request.args.get("duration_mode", default=30, type=int)
    if duration_mode not in (15, 30, 60):
        duration_mode = 30

    db = get_db()
    cursor = db.cursor()

    top_scores = db.execute(
        """
        SELECT users.username, races.wpm, races.accuracy, races.completed_at
        FROM races
        JOIN users ON races.user_id = users.id
        where races.duration_mode = ?
        ORDER BY races.wpm DESC
        LIMIT 10
        """,
        (duration_mode, )
    ).fetchall()

    db.close()

    return render_template("leaderboard.html", scores = top_scores, current_mode = duration_mode)


@app.route("/history")
@login_required
def history():

    db = get_db()
    cursor = db.cursor()

    races = db.execute(
        "SELECT duration_mode, wpm, accuracy, completed_at FROM races WHERE user_id = ? ORDER BY completed_at DESC",
        (session["user_id"],)
    ).fetchall()
    db.close()

    return render_template("history.html", races=races)
