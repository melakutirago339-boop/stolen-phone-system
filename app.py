from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Stolen Phone Tracking & Recovery System"

if __name__ == "__main__":
    app.run(debug=True)
