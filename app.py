from flask import Flask, render_template, request, redirect, session
import os
import psycopg2

app = Flask(__name__)

app.secret_key = "change-this-secret-key"


# =========================
# DATABASE CONNECTION
# =========================
def get_db_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])


# =========================
# CREATE DATABASE TABLE
# =========================
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stolen_phones (
            id SERIAL PRIMARY KEY,
            owner_name VARCHAR(100) NOT NULL,
            phone_number VARCHAR(30),
            phone_model VARCHAR(100),
            imei VARCHAR(50) NOT NULL UNIQUE,
            date_stolen DATE,
            location VARCHAR(200),
            description TEXT,
            status VARCHAR(30) DEFAULT 'Stolen',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return redirect("/login")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        if username == "admin" and password == "admin123":

            session["username"] = username
            session["role"] = role

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"]
    )


# =========================
# DATABASE TEST
# =========================
@app.route("/db-test")
def db_test():

    try:
        conn = get_db_connection()
        conn.close()

        return "Database connection successful ✅"

    except Exception as e:

        return f"Database connection failed ❌: {e}"


# =========================
# REPORT STOLEN PHONE
# =========================
@app.route("/report", methods=["GET", "POST"])
def report():

    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":

        owner_name = request.form.get("owner_name")
        phone_number = request.form.get("phone_number")
        phone_model = request.form.get("phone_model")
        imei = request.form.get("imei")
        date_stolen = request.form.get("date_stolen")
        location = request.form.get("location")
        description = request.form.get("description")

        try:

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO stolen_phones
                (owner_name, phone_number, phone_model, imei,
                 date_stolen, location, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                owner_name,
                phone_number,
                phone_model,
                imei,
                date_stolen,
                location,
                description
            ))

            conn.commit()

            cur.close()
            conn.close()

            return render_template(
                "report.html",
                success="Phone report saved successfully ✅"
            )

        except psycopg2.errors.UniqueViolation:

            return render_template(
                "report.html",
                error="This IMEI is already registered ❌"
            )

        except Exception as e:

            return render_template(
                "report.html",
                error=f"Database error ❌: {e}"
            )

    return render_template("report.html")


# =========================
# SEARCH BY IMEI
# =========================
@app.route("/search", methods=["GET", "POST"])
def search():

    if "username" not in session:
        return redirect("/login")

    phone = None
    error = None

    if request.method == "POST":

        imei = request.form.get("imei")

        try:

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT id, owner_name, phone_number, phone_model,
                       imei, date_stolen, location, description,
                       status, created_at
                FROM stolen_phones
                WHERE imei = %s
            """, (imei,))

            phone = cur.fetchone()

            cur.close()
            conn.close()

            if phone is None:
                error = "No stolen phone found with this IMEI ❌"

        except Exception as e:

            error = f"Database error ❌: {e}"

    return render_template(
        "search.html",
        phone=phone,
        error=error
    )


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================
# START APP
# =========================
if __name__ == "__main__":

    try:
        create_table()
        print("Database table ready ✅")

    except Exception as e:
        print("Database table error:", e)

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
