import json, random, time, sys, subprocess, os, shutil, copy, requests, datetime
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint, send_file, session
from flask_cors import CORS
from models import *
from dotenv import load_dotenv
from admin.analytics import Analytics
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
    # Boot pre-processing

    ## Set up DatabaseInterface
    response = DI.setup()
    if response != "Success":
        print("MAIN BOOT: Error in setting up DI; error: " + response)
        sys.exit(1)
    else:
        print("DI: Setup complete.")

    ## Set up AddonsManager
    response = AddonsManager.setup()
    if response != "Success":
        print("MAIN BOOT: Error in setting up AddonsManager; error: " + response)
        sys.exit(1)
    else:
        print("ADDONSMANAGER: Setup complete.")

    ## Set up FireAuth
    response = FireAuth.connect()
    if not response:
        print("MAIN BOOT: Failed to establish FireAuth connection. Boot aborted.")
        sys.exit(1)
    else:
        print("FIREAUTH: Setup complete.")
    
    ## Set up Analytics
    Analytics.setup()
    
    ## Set up Logger
    Logger.setup()
    
    # Register routes
    
    ## Generation routes
    from generation.itineraryGeneration import itineraryGenBP
    app.register_blueprint(itineraryGenBP)
    
    ## Admin routes
    from admin.report import reportBP
    app.register_blueprint(reportBP)
    
    ## Forum routes
    from forum.forum import forumBP
    app.register_blueprint(forumBP)

    ## Editor routes
    from editor.editor import editorPage
    app.register_blueprint(editorPage)

    ## Completion routes
    from editor.completion import completionPage
    app.register_blueprint(completionPage)

    ## Account route
    from identity.accounts import accountsBP
    app.register_blueprint(accountsBP)

    ## API routes
    from api import apiBP
    app.register_blueprint(apiBP)

    ## Assets service
    from assets import assetsBP
    app.register_blueprint(assetsBP)

    print()
    print("All services online; boot pre-processing and setup complete.")
    print("Booting Verdex...")

    app.run(port=8000, host='0.0.0.0')