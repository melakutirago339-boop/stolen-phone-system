```python
from flask import Flask, render_template, request, redirect, session
import os
import psycopg2

app = Flask(__name__)

# =========================
# SECRET KEY
# =========================
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "stolen-phone-system-secret-key"
)


# =========================
# DATABASE CONNECTION
# =========================
def get_db_connection():
    return psycopg2.connect(
        os.environ["DATABASE_URL"]
    )


# =========================
# CREATE DATABASE TABLES
# =========================
def create_tables():

    conn = get_db_connection()
    cur = conn.cursor()

    # Registered phones
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registered_phones (
            id SERIAL PRIMARY KEY,
            owner_name VARCHAR(100) NOT NULL,
            phone_number VARCHAR(50),
            phone_model VARCHAR(100),
            imei VARCHAR(50) NOT NULL UNIQUE,
            phone_color VARCHAR(50),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Stolen phones
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stolen_phones (
            id SERIAL PRIMARY KEY,
            owner_name VARCHAR(100) NOT NULL,
            phone_number VARCHAR(50),
            phone_model VARCHAR(100),
            imei VARCHAR(50) NOT NULL UNIQUE,
            date_stolen DATE,
            location TEXT,
            description TEXT,
            status VARCHAR(30) DEFAULT 'Stolen',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Cases
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id SERIAL PRIMARY KEY,
            imei VARCHAR(50) NOT NULL,
            case_number VARCHAR(100),
            officer_name VARCHAR(100),
            case_status VARCHAR(50) DEFAULT 'Open',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Authorized locations
    cur.execute("""
        CREATE TABLE IF NOT EXISTS authorized_locations (
            id SERIAL PRIMARY KEY,
            location_name VARCHAR(150) NOT NULL,
            address TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    cur.close()
    conn.close()


# =========================
# START DATABASE
# =========================
try:
    create_tables()
    print("Database tables ready ✅")

except Exception as e:
    print("Database table error:", e)


# =========================
# HOME
# =========================
@app.route("/")
def home():

    if "username" in session:
        return redirect("/dashboard")

    return redirect("/login")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role", "admin")

        # Demo login
        if username == "admin" and password == "admin123":

            session["username"] = username
            session["role"] = role

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid username or password ❌"
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
        cur = conn.cursor()

        cur.execute("SELECT 1")

        cur.close()
        conn.close()

        return "Database connection successful ✅"

    except Exception as e:

        return f"Database connection failed ❌: {e}"


# =========================
# REGISTER PHONE
# =========================
@app.route("/register_phone", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def register_phone():

    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":

        owner_name = request.form.get("owner_name")
        phone_number = request.form.get("phone_number")
        phone_model = request.form.get("phone_model")
        imei = request.form.get("imei")
        phone_color = request.form.get("phone_color")
        description = request.form.get("description")

        try:

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO registered_phones
                (
                    owner_name,
                    phone_number,
                    phone_model,
                    imei,
                    phone_color,
                    description
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                owner_name,
                phone_number,
                phone_model,
                imei,
                phone_color,
                description
            ))

            conn.commit()

            cur.close()
            conn.close()

            return render_template(
                "register_phone.html",
                success="Phone registered successfully ✅"
            )

        except psycopg2.errors.UniqueViolation:

            return render_template(
                "register_phone.html",
                error="This IMEI is already registered ❌"
            )

        except Exception as e:

            return render_template(
                "register_phone.html",
                error=f"Database error ❌: {e}"
            )

    return render_template("register_phone.html")


# =========================
# REPORT STOLEN PHONE
# =========================
@app.route("/report_stolen", methods=["GET", "POST"])
@app.route("/report", methods=["GET", "POST"])
def report_stolen():

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
                (
                    owner_name,
                    phone_number,
                    phone_model,
                    imei,
                    date_stolen,
                    location,
                    description
                )
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
                error="This IMEI is already reported ❌"
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
@app.route("/search_imei", methods=["GET", "POST"])
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

            # First search stolen phone
            cur.execute("""
                SELECT
                    id,
                    owner_name,
                    phone_number,
                    phone_model,
                    imei,
                    date_stolen,
                    location,
                    description,
                    status,
                    created_at
                FROM stolen_phones
                WHERE imei = %s
            """, (imei,))

            phone = cur.fetchone()

            # If not stolen, search registered phone
            if phone is None:

                cur.execute("""
                    SELECT
                        id,
                        owner_name,
                        phone_number,
                        phone_model,
                        imei,
                        NULL,
                        NULL,
                        description,
                        'Registered',
                        created_at
                    FROM registered_phones
                    WHERE imei = %s
                """, (imei,))

                phone = cur.fetchone()

            cur.close()
            conn.close()

            if phone is None:
                error = "No phone found with this IMEI ❌"

        except Exception as e:

            error = f"Database error ❌: {e}"

    return render_template(
        "search.html",
        phone=phone,
        error=error
    )


# =========================
# CASE MANAGEMENT
# =========================
@app.route("/cases", methods=["GET", "POST"])
def cases():

    if "username" not in session:
        return redirect("/login")

    message = None
    error = None

    if request.method == "POST":

        imei = request.form.get("imei")
        case_number = request.form.get("case_number")
        officer_name = request.form.get("officer_name")
        case_status = request.form.get("case_status", "Open")
        notes = request.form.get("notes")

        try:

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO cases
                (
                    imei,
                    case_number,
                    officer_name,
                    case_status,
                    notes
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                imei,
                case_number,
                officer_name,
                case_status,
                notes
            ))

            conn.commit()

            cur.close()
            conn.close()

            message = "Case saved successfully ✅"

        except Exception as e:

            error = f"Database error ❌: {e}"

    return render_template(
        "cases.html",
        message=message,
        error=error
    )


# =========================
# AUTHORIZED LOCATION
# =========================
@app.route("/location", methods=["GET", "POST"])
def location():

    if "username" not in session:
        return redirect("/login")

    message = None
    error = None

    if request.method == "POST":

        location_name = request.form.get("location_name")
        address = request.form.get("address")
        description = request.form.get("description")

        try:

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO authorized_locations
                (
                    location_name,
                    address,
                    description
                )
                VALUES (%s, %s, %s)
            """, (
                location_name,
                address,
                description
            ))

            conn.commit()

            cur.close()
            conn.close()

            message = "Location saved successfully ✅"

        except Exception as e:

            error = f"Database error ❌: {e}"

    return render_template(
        "location.html",
        message=message,
        error=error
    )


# =========================
# REPORTS
# =========================
@app.route("/reports")
def reports():

    if "username" not in session:
        return redirect("/login")

    try:

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT COUNT(*) FROM registered_phones"
        )
        registered_count = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM stolen_phones"
        )
        stolen_count = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM cases"
        )
        cases_count = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM authorized_locations"
        )
        location_count = cur.fetchone()[0]

        cur.close()
        conn.close()

        return render_template(
            "reports.html",
            registered_count=registered_count,
            stolen_count=stolen_count,
            cases_count=cases_count,
            location_count=location_count
        )

    except Exception as e:

        return render_template(
            "reports.html",
            error=f"Database error ❌: {e}"
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

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
```
