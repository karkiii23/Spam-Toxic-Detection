import csv
import io
import os
import re
import sqlite3
import time
from functools import wraps

import joblib
import nltk
import psycopg
from flask import (
    Flask,
    Response,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from nltk.corpus import stopwords
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "1234spam"

# ============================================================
# DATABASE
# ============================================================

DATABASE = "database/users.db"


def get_db():

    # timeout: wait up to 10 seconds if another connection holds the lock
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row

    return conn


# PostgreSQL connection helper
DATABASE_URL = "postgresql://spam_toxic_db_user:Uz1iWznUs00CeNCYAU8rtKRp8KNwu5hT@dpg-db495rm0tbcc73djie50-a.singapore-postgres.render.com/spam_toxic_db"


def get_db_connection():

    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured.")

    return psycopg.connect(
        DATABASE_URL,
        sslmode="require"
    )


def init_database():

    os.makedirs("database", exist_ok=True)

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL

        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            message TEXT NOT NULL,

            spam_result TEXT NOT NULL,

            toxic_result TEXT NOT NULL,

            overall_result TEXT NOT NULL,

            analysis_type TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
            REFERENCES users(id)

        )
    """)

    conn.commit()

    conn.close()


init_database()


# ============================================================
# LOGIN PROTECTION
# ============================================================

def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return decorated_function


# ============================================================
# LOAD MODELS
# ============================================================

spam_model = joblib.load("models/spam_model.pkl")
spam_vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
toxic_model = joblib.load("models/toxic_model.pkl")
toxic_vectorizer = joblib.load("models/toxic_tfidf_vectorizer.pkl")


# ============================================================
# STOPWORDS
# ============================================================

try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    text = str(text).lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)

    # Remove special characters and numbers
    text = re.sub(r"[^a-zA-Z\s]", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Remove stopwords
    words = [word for word in text.split() if word not in stop_words]

    return " ".join(words)


# ============================================================
# MESSAGE ANALYSIS
# ============================================================

def analyze_message(message):

    message = str(message).strip()

    if not message:
        return {
            "spam": "NORMAL",
            "toxic": "NORMAL",
            "overall": "SAFE"
        }

    # SPAM PREDICTION
    spam_text = spam_vectorizer.transform([message])
    spam_prediction = spam_model.predict(spam_text)[0]
    spam_result = "SPAM" if spam_prediction == 1 else "NORMAL"

    # TOXIC PREDICTION
    toxic_text = toxic_vectorizer.transform([message])
    toxic_prediction = toxic_model.predict(toxic_text)[0]
    toxic_result = "TOXIC" if toxic_prediction == 1 else "NORMAL"

    # OVERALL RESULT
    if spam_result == "SPAM" and toxic_result == "TOXIC":
        overall_result = "SPAM + TOXIC"
    elif spam_result == "SPAM":
        overall_result = "SPAM DETECTED"
    elif toxic_result == "TOXIC":
        overall_result = "TOXIC CONTENT"
    else:
        overall_result = "SAFE"

    return {
        "spam": spam_result,
        "toxic": toxic_result,
        "overall": overall_result
    }


# ============================================================
# SAVE TO DATABASE
# ============================================================

def save_analysis(message, result, analysis_type="Single"):

    user_id = session.get("user_id")

    if not user_id:
        return

    conn = get_db()

    conn.execute(
        """
        INSERT INTO analysis_history
        (
            user_id,
            message,
            spam_result,
            toxic_result,
            overall_result,
            analysis_type
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            message,
            result["spam"],
            result["toxic"],
            result["overall"],
            analysis_type
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            return render_template(
                "register.html",
                error="All fields are required."
            )

        if len(password) < 6:
            return render_template(
                "register.html",
                error="Password must contain at least 6 characters."
            )

        conn = get_db()

        try:
            hashed_password = generate_password_hash(password)

            conn.execute(
                """
                INSERT INTO users
                (username, email, password)
                VALUES (?, ?, ?)
                """,
                (username, email, hashed_password)
            )

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()

            return render_template(
                "register.html",
                error="Username or email already exists."
            )

        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid username or password."
        )

    return render_template("login.html")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ============================================================
# HOME
# ============================================================

@app.route("/")
@login_required
def home():

    mode = request.args.get("mode", "single")

    return render_template(
        "index.html",
        mode=mode
    )


# ============================================================
# SINGLE MESSAGE ANALYSIS
# ============================================================

@app.route("/predict", methods=["POST"])
@login_required
def predict():

    message = request.form.get("message", "").strip()

    if not message:
        return render_template(
            "index.html",
            error="Please enter a message.",
            mode="single"
        )

    time.sleep(20)  # 20-second delay

    result = analyze_message(message)

    save_analysis(message, result, "Single")

    return render_template(
        "index.html",
        message=message,
        spam_result=result["spam"],
        toxic_result=result["toxic"],
        overall_result=result["overall"],
        mode="single"
    )


# ============================================================
# BATCH ANALYSIS
# ============================================================

@app.route("/batch", methods=["POST"])
@login_required
def batch():

    batch_text = request.form.get("batch_messages", "").strip()

    if not batch_text:
        return render_template(
            "index.html",
            error="Please enter at least one message.",
            mode="batch"
        )

    time.sleep(20)  # 20-second delay

    # One message per line
    messages = [
        line.strip()
        for line in batch_text.splitlines()
        if line.strip()
    ]

    results = []

    for number, message in enumerate(messages, start=1):

        result = analyze_message(message)

        results.append({
            "id": number,
            "message": message,
            "spam": result["spam"],
            "toxic": result["toxic"],
            "overall": result["overall"]
        })

    # Save in reverse so the first message in the batch
    # has the highest id and appears at the top of the dashboard
    for item in reversed(results):
        save_analysis(
            item["message"],
            {
                "spam": item["spam"],
                "toxic": item["toxic"],
                "overall": item["overall"]
            },
            "Batch"
        )

    return render_template(
        "index.html",
        batch_results=results,
        batch_count=len(results),
        mode="batch"
    )


# ============================================================
# DOWNLOAD BATCH RESULTS
# ============================================================

@app.route("/download", methods=["POST"])
@login_required
def download():

    batch_text = request.form.get("batch_messages", "").strip()

    messages = [
        line.strip()
        for line in batch_text.splitlines()
        if line.strip()
    ]

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Message",
        "Spam Detection",
        "Toxic Detection",
        "Overall Result"
    ])

    for number, message in enumerate(messages, start=1):

        result = analyze_message(message)

        writer.writerow([
            number,
            message,
            result["spam"],
            result["toxic"],
            result["overall"]
        ])

    response = Response(
        output.getvalue(),
        mimetype="text/csv"
    )

    response.headers["Content-Disposition"] = "attachment; filename=analysis_results.csv"

    return response


# ============================================================
# DASHBOARD PAGE
# ============================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user_id = session["user_id"]

    conn = get_db()

    history = conn.execute(
        """
        SELECT
            id,
            message,
            spam_result,
            toxic_result,
            overall_result,
            analysis_type,
            created_at

        FROM analysis_history

        WHERE user_id = ?

        ORDER BY id DESC
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    total = len(history)

    spam_count = sum(
        1 for item in history
        if item["spam_result"] == "SPAM"
    )

    toxic_count = sum(
        1 for item in history
        if item["toxic_result"] == "TOXIC"
    )

    safe_count = sum(
        1 for item in history
        if item["overall_result"] == "SAFE"
    )

    return render_template(
        "dashboard.html",
        history=history,
        total=total,
        spam_count=spam_count,
        toxic_count=toxic_count,
        safe_count=safe_count
    )


# ============================================================
# HISTORY PAGE (all records for the logged-in user)
# ============================================================

@app.route("/history")
@login_required
def history():

    user_id = session["user_id"]

    conn = get_db()

    records = conn.execute(
        """
        SELECT
            id,
            message,
            spam_result,
            toxic_result,
            overall_result,
            analysis_type,
            created_at

        FROM analysis_history

        WHERE user_id = ?

        ORDER BY id DESC
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "history.html",
        records=records
    )


# ============================================================
# MY ACCOUNT
# ============================================================

@app.route("/account")
@login_required
def account():

    user_id = session["user_id"]

    conn = get_db()

    user = conn.execute(
        """
        SELECT username, email
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "account.html",
        user=user
    )


# ============================================================
# SWITCH ACCOUNT (clears the login session only; data is kept)
# ============================================================

@app.route("/switch-account")
def switch_account():

    session.clear()

    return redirect(url_for("login"))


# ============================================================
# CLEAR DASHBOARD HISTORY (current user only)
# ============================================================

@app.route("/clear-history", methods=["POST"])
@login_required
def clear_history():

    user_id = session["user_id"]

    conn = get_db()

    conn.execute(
        """
        DELETE FROM analysis_history
        WHERE user_id = ?
        """,
        (user_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    init_database()

    app.run(
        debug=True
    )