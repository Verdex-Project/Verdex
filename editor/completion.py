from flask import Flask,render_template,Blueprint
from flask_cors import CORS

completionPage = Blueprint("completionPageBP",__name__)

@completionPage.route("/completion")
def completion():
    return render_template("editor/completion.html")

