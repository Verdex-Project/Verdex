# refer to prakhar main file

from flask import Flask,render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/editor")
def editor():
    return render_template("editor.html")
