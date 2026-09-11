from flask import Flask, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

import sqlite3

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

        return render_template("index.html", username=username)

    return render_template("login.html")
