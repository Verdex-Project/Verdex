from flask import Flask,render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/completion")
def completion():
    return render_template("completion.html")
