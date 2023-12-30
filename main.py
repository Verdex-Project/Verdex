import json, random, time, sys, subprocess, os, shutil, copy, requests, datetime
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint, send_file
from flask_cors import CORS
from models import *
from dotenv import load_dotenv

#Added these imports for report and forum blueprints
from report import report_display_page
from forum import verdextalks_page

load_dotenv()

app = Flask(__name__)
CORS(app)

#Register blueprint for main report webpage
app.register_blueprint(report_display_page, url_prefix="/report")

#Register blueprint for VerdexTalks webpage
app.register_blueprint(verdextalks_page, url_prefix="/verdextalks")

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

    # Register routes

    ## Assets service
    from assets import assetsBP
    app.register_blueprint(assetsBP)

    print()
    print("All services online; boot pre-processing and setup complete.")
    print("Booting Verdex...")

    app.run(port=8000, host='0.0.0.0')

# if not os.path.isfile(os.path.join(os.getcwd(), "reports", "report-{}.txt".format(report_id))):
#     return "ERROR: Report file was not found."