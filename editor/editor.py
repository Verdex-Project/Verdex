from flask import Flask,render_template,Blueprint
from flask_cors import CORS

editorPage = Blueprint("editorPageBP",__name__)

@editorPage.route("/editor")
def editor():
    return render_template("editor/editor.html")
