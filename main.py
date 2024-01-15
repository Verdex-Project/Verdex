import json, random, time, sys, subprocess, os, shutil, copy, requests, datetime
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint, send_file, session
from flask_cors import CORS
from models import *
from dotenv import load_dotenv
from admin.analytics import Analytics
load_dotenv()

app = Flask(__name__)
CORS(app)

## Configure app
app.secret_key = os.environ['AppSecretKey']

## Global methods
def deleteSession(accountID):
    if accountID not in DI.data["accounts"]:
        return False
    
    if "idToken" in DI.data["accounts"][accountID]:
        del DI.data["accounts"][accountID]["idToken"]
    if "refreshToken" in DI.data["accounts"][accountID]:
        del DI.data["accounts"][accountID]["refreshToken"]
    if "tokenExpiry" in DI.data["accounts"][accountID]:
        del DI.data["accounts"][accountID]["tokenExpiry"]
    DI.save()

    return True

def manageIDToken(checkIfAdmin=False):
    '''Returns account ID if token is valid (will refresh if expiring soon) and a str error message if not valid.'''

    if "idToken" not in session:
        return "ERROR: Please sign in first."
    
    for accountID in DI.data["accounts"]:
        if "idToken" not in DI.data["accounts"][accountID]:
            # This account doesn't have an ID token, so
            continue
        elif DI.data["accounts"][accountID]["idToken"] == session["idToken"]:
            delta = datetime.datetime.strptime(DI.data["accounts"][accountID]["tokenExpiry"], Universal.systemWideStringDatetimeFormat) - datetime.datetime.now()
            if delta.total_seconds() < 0:
                deleteSession(accountID)
                del session["idToken"]
                Logger.log("MANAGEIDTOKEN: Session expired for account with ID '{}'.".format(accountID))
                return "ERROR: Your session has expired. Please sign in again."
            elif delta.total_seconds() < 600:
                # Refresh token if it's less than 10 minutes from expiring
                response = FireAuth.refreshToken(DI.data["accounts"][accountID]["refreshToken"])
                if isinstance(response, str):
                    # Refresh token is invalid, delete session entirely
                    deleteSession(accountID)
                    del session["idToken"]
                    return "ERROR: Your session expired. Please sign in again."
                
                DI.data["accounts"][accountID]["idToken"] = response["idToken"]
                DI.data["accounts"][accountID]["refreshToken"] = response["refreshToken"]
                DI.data["accounts"][accountID]["tokenExpiry"] = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat)
                DI.save()

                Logger.log("MANAGEIDTOKEN: Refreshed token for account with ID '{}'.".format(accountID))

                session["idToken"] = response["idToken"]

                if checkIfAdmin:
                    if not ("admin" in DI.data["accounts"][accountID] and DI.data["accounts"][accountID]["admin"] == True):
                        return "ERROR: Access forbidden due to insufficient permissions."

            return "SUCCESS: {}".format(accountID)
    
    # If we get here, the session is invalid as the ID token is not in the database
    del session["idToken"]
    return "ERROR: Invalid credentials."

@app.before_request
def updateAnalytics():
    Analytics.add_metrics('get_request' if request.method == "GET" else "post_request")
    return

@app.route('/')
def homepage():
    if "generateReport" in request.args and request.args["generateReport"] == "true":
        Analytics.generateReport()
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

    ## Set up FireConn
    if FireConn.checkPermissions():
        response = FireConn.connect()
        if response != True:
            print("MAIN BOOT: Error in setting up FireConn; error: " + response)
            sys.exit(1)
        else:
            print("FIRECONN: Firebase connection established.")

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

    # Database Synchronisation with Firebase Auth accounts
    if FireConn.checkPermissions():
        previousCopy = copy.deepcopy(DI.data["accounts"])
        DI.data["accounts"] = FireAuth.generateAccountsObject(fireAuthUsers=FireAuth.listUsers(), existingAccounts=DI.data["accounts"], strategy="overwrite")
        DI.save()

        if previousCopy != DI.data["accounts"]:
            print("MAIN: Necessary database synchronisation with Firebase Authentication complete.")
    
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