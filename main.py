import json, random, time, sys, subprocess, os, shutil, copy, requests, datetime
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint
from flask_cors import CORS
from models import *
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

app.secret_key = os.environ['AppSecretKey']

@app.route('/')
def homepage():
    return render_template('homepage.html')

# Security pages
@app.route('/security/error')
def error():
    if 'error' not in request.args:
        return render_template("error.html", error=None, originURL=request.host_url)
    else:
        return render_template("error.html", error=request.args["error"], originURL=request.host_url)
    
@app.route("/security/unauthorised")
def unauthorised():
    if "error" not in request.args:
        return render_template("unauthorised.html", message="No error message was provided.", originURL=request.host_url)
    return render_template("unauthorised.html", message=request.args["error"], originURL=request.host_url)

## Make a 404 route
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error="404: Page not found.", originURL=request.host_url)

if __name__ == '__main__':
    # Register routes

    ## Assets service
    from assets import assetsBP
    app.register_blueprint(assetsBP)

    app.run(port=8000, host='0.0.0.0', debug=True)