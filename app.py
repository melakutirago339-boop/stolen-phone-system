from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)

app.secret_key = "change-this-secret-key"


@app.route("/")
def home():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        # Temporary test login
        if username == "admin" and password == "admin123":

            session["username"] = username
            session["role"] = role

            return redirect("/dashboard")

        return "Invalid username or password"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    return f"""
    <h1>Stolen Phone Recovery Dashboard</h1>

    <p>Welcome, {session["username"]}</p>

    <p>Role: {session["role"]}</p>

    <hr>

    <h2>System Modules</h2>

    <ul>
        <li>Register Phone</li>
        <li>Report Stolen Phone</li>
        <li>Search by IMEI</li>
        <li>Case Management</li>
        <li>Authorized Location Data</li>
        <li>Reports</li>
    </ul>
    """


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
