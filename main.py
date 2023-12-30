import json, random, time, sys, subprocess, os, shutil, copy, requests, datetime
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint, send_file
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

#Added this for report generation
@app.route('/report')
def report():
    with open('test_data.json', 'r') as file:
        data = json.load(file)
    return render_template('report.html', data=data)
#End

#Added this for report downloading feature
@app.route('/download_report', methods=['POST'])
def download_report():
    report_id = request.form['report_id']
    with open('test_data.json', 'r') as file:
        data = json.load(file)

    if report_id in data:
        report_data = data[report_id]
        with open('downloaded_report.txt', 'w') as report_file:
            for key, value in report_data.items():
                report_file.write(f"{key}: {value}\n")
        return send_file('downloaded_report.txt', as_attachment=True)
    else:
        return "Error: Report ID not found."
#End

#Added this for forum
@app.route('/verdextalks')
def verdextalks():
    return render_template('forum/forum.html')

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