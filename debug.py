from flask import Flask, request, Blueprint, render_template, redirect, url_for, jsonify
from main import DI, Logger, Universal, FireConn, FireAuth, FireRTDB, AddonsManager, Analytics, Encryption, FolderManager
import os, sys, json, datetime, copy, shutil

debugBP = Blueprint("debug", __name__)

debugMode = os.environ.get("DebugMode") == "True"

@debugBP.route("/debug/<secretKey>")
def debugHome(secretKey):
    if not debugMode:
        return redirect(url_for('unauthorised', error="Debug mode is not enabled."))
    if secretKey != os.environ.get("AppSecretKey"):
        return redirect(url_for('unauthorised', error="Invalid credentials."))
    
    options = """
Options:<br><br>
- View logs: /debug/[key]/logs<br>
- Clear logs: /debug/[key]/logs/clear<br>
- Reload DI: /debug/[key]/reloadDI<br>
- FireAuth sync: /debug/[key]/fireAuthSync<br>
- FireReset: /debug/[key]/fireReset (Wipes all Firebase data, including Firebase Auth accounts, and reloads DI. Use with caution.)<br>
- Toggle usage lock: /debug/[key]/toggleUsageLock<br>
- Create admin: /debug/[key]/createAdmin?email=[email]&password=[password]<br>
- Toggle GPT: /debug/[key]/toggleGPT<br>
- Presentation transform: /debug/[key]/presentationTransform (Wipes all data and creates a new Google login user, with sample post, and admin account. Use with extreme caution.)<br>
    """
    
    return options

@debugBP.route("/debug/<secretKey>/logs")
def viewLogs(secretKey):
    if not debugMode:
        return redirect(url_for('unauthorised', error="Debug mode is not enabled."))
    if secretKey != os.environ.get("AppSecretKey"):
        return redirect(url_for('unauthorised', error="Invalid credentials."))
    
    return "<br>".join(Logger.readAll())

@debugBP.route("/debug/<secretKey>/logs/clear")
def clearLogs(secretKey):
    if not debugMode:
        return redirect(url_for('unauthorised', error="Debug mode is not enabled."))
    if secretKey != os.environ.get("AppSecretKey"):
        return redirect(url_for('unauthorised', error="Invalid credentials."))
    
    Logger.destroyAll()
    return "Logs cleared."

@debugBP.route("/debug/<secretKey>/reloadDI")
def reloadDI(secretKey):
    if not debugMode:
        return redirect(url_for('unauthorised', error="Debug mode is not enabled."))
    if secretKey != os.environ.get("AppSecretKey"):
        return redirect(url_for('unauthorised', error="Invalid credentials."))
    
    DI.load()

    Logger.log("DEBUG RELOADDI: DI reloaded.")
    return "DI reload success. DI sync status: {}".format(DI.syncStatus)

@debugBP.route("/debug/<secretKey>/fireAuthSync")
def fireAuthSync(secretKey):
    if not debugMode:
        return redirect(url_for('unauthorised', error="Debug mode is not enabled."))
    if secretKey != os.environ.get("AppSecretKey"):
        return redirect(url_for('unauthorised', error="Invalid credentials."))
    
    try:
        if FireConn.checkPermissions():
            previousCopy = copy.deepcopy(DI.data["accounts"])
            DI.data["accounts"] = FireAuth.generateAccountsObject(fireAuthUsers=FireAuth.listUsers(), existingAccounts=DI.data["accounts"], strategy="overwrite")
            DI.save()

            if previousCopy != DI.data["accounts"]:
                return "FireAuth sync success. Accounts object updated with changes."
            else:
                return "FireAuth sync success. No changes detected."
        else:
            return "FireAuth sync failed. FireConn is not enabled."
    except Exception as e:
        return "FireAuth sync failed. Error: {}".format(e)
    
@debugBP.route("/debug/<secretKey>/fireReset")
def fireReset(secretKey):
    if not debugMode:
        return redirect(url_for('unauthorised', error="Debug mode is not enabled."))
    if secretKey != os.environ.get("AppSecretKey"):
        return redirect(url_for('unauthorised', error="Invalid credentials."))
    
    try:
        for fireUser in FireAuth.listUsers():
            FireAuth.deleteAccount(fireUser.uid, admin=True)
        
        FireRTDB.setRef({})
        DI.load()
    except Exception as e:
        return "Firebase reset failed. Error: {}".format(e)
    
    Logger.log("DEBUG FIRERESET: All Firebase RTDB and Auth data wiped. DI reloaded.")

    return "Firebase reset success. Accounts and database data wiped."

@debugBP.route("/debug/<secretKey>/toggleUsageLock")
def toggleUsageLock(secretKey):
    if not debugMode:
        return redirect(url_for('unauthorised', error="Debug mode is not enabled."))
    if secretKey != os.environ.get("AppSecretKey"):
        return redirect(url_for('unauthorised', error="Invalid credentials."))
    
    currentStatus = AddonsManager.readConfigKey("UsageLock") == True
    AddonsManager.setConfigKey("UsageLock", not currentStatus)

    Logger.log("DEBUG TOGGLEUSAGELOCK: Usage lock status toggled to {}.".format("True" if (not currentStatus) else "False"))
    return "Usage lock status toggled to {}.".format("True" if (not currentStatus) else "False")

@debugBP.route("/debug/<secretKey>/createAdmin")
def createAdmin(secretKey):
    if not debugMode:
        return redirect(url_for('unauthorised', error="Debug mode is not enabled."))
    if secretKey != os.environ.get("AppSecretKey"):
        return redirect(url_for('unauthorised', error="Invalid credentials."))
    if "email" not in request.args:
        return "Please provide an email."
    if "password" not in request.args:
        return "Please provide a password."
    
    email = request.args.get("email")
    password = request.args.get("password")
    username = Analytics.generateRandomID(customLength=5)

    accID = Universal.generateUniqueID()
    responseObject = FireAuth.createUser(email=email, password=password)
    if "ERROR" in responseObject:
        return "Error: {}".format(responseObject)
    
    DI.data["accounts"][accID] = {
        "id": accID,
        "fireAuthID": responseObject["uid"],
        "username": username,
        "email": email,
        "password": Encryption.encodeToSHA256(password),
        "idToken": responseObject["idToken"],
        "refreshToken": responseObject["refreshToken"],
        "tokenExpiry": (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat),
        "disabled": False,
        "admin": True,
        "name": "Admin",
        "position": "Debug Admin",
        "aboutMe": ""
    }
    Logger.log("DEBUG CREATEADMIN: Created admin account with ID {}.".format(accID))
    DI.save()

    return "Admin account created with that email and password. ID: {}, Username: {}".format(accID, username)

@debugBP.route("/debug/<secretKey>/toggleGPT")
def toggleGPT(secretKey):
    if not debugMode:
        return redirect(url_for('unauthorised', error="Debug mode is not enabled."))
    if secretKey != os.environ.get("AppSecretKey"):
        return redirect(url_for('unauthorised', error="Invalid credentials."))
    
    currentStatus = AddonsManager.readConfigKey("VerdexGPTEnabled") == True
    AddonsManager.setConfigKey("VerdexGPTEnabled", not currentStatus)

    Logger.log("DEBUG TOGGLEGPT: GPT status toggled to {}.".format("True" if (not currentStatus) else "False"))
    return "VerdexGPT status toggled to {}.".format("True" if (not currentStatus) else "False")

@debugBP.route("/debug/<secretKey>/presentationTransform", methods=["GET", "POST"])
def presentationTransform(secretKey):
    if not debugMode:
        return redirect(url_for('unauthorised', error="Debug mode is not enabled."))
    if secretKey != os.environ.get("AppSecretKey"):
        return redirect(url_for('unauthorised', error="Invalid credentials."))
    
    if request.method == "GET":
        return render_template("presentationTransform.html", secretKey=secretKey)
    
    ## POST
    if "userEmail" not in request.form:
        return "Please provide a user email."
    # if "userPassword" not in request.form:
    #     return "Please provide a user password."
    if "adminEmail" not in request.form:
        return "Please provide an admin email."
    if "adminPassword" not in request.form:
        return "Please provide an admin password."
    if "supportQueryEmail" not in request.form:
        return "Please provide a support query email (query reply will be sent to this email)."
    
    # Wipe all data
    
    ## Clear Firebase Authentication accounts
    try:
        for fireUser in FireAuth.listUsers():
            FireAuth.deleteAccount(fireUser.uid, admin=True)
    except Exception as e:
        Logger.log("DEBUG PRESENTATIONTRANSFORM ERROR: Firebase Authentication reset failed. Error: {}".format(e))
        return "Firebase Authentication reset failed. Error: {}".format(e)
    
    ## Clear DI
    try:
        DI.data = copy.deepcopy(DI.sampleData)
        DI.save()
    except Exception as e:
        Logger.log("DEBUG PRESENTATIONTRANSFORM ERROR: DI reload failed. Error: {}".format(e))
        return "DI reload failed. Error: {}".format(e)
    
    ## Create new user account
    userAccEmail = request.form.get("userEmail")
    userAccID = Universal.generateUniqueID()
    userAccResponse = FireAuth.createUser(email=userAccEmail, password="googlelogin")
    if "ERROR" in userAccResponse:
        Logger.log("DEBUG PRESENTATIONTRANSFORM ERROR: User account creation failed. Error: {}".format(userAccResponse))
        return "User account creation failed. Error: {}".format(userAccResponse)
    
    DI.data["accounts"][userAccID] = {
        "id": userAccID,
        "fireAuthID": userAccResponse["uid"],
        "googleLogin": True,
        "username": "john",
        "email": userAccEmail,
        "password": Encryption.encodeToSHA256("googlelogin"),
        "idToken": userAccResponse['idToken'],
        "refreshToken": userAccResponse['refreshToken'],
        "tokenExpiry": (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat),
        "disabled": False,
        "admin": False,
        "forumBanned": False,
        "aboutMe": "",
        "reports": {}
    }

    ## Attach sample forum post to user account
    newPostDatetime = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
    newPost = {
        "username": "john",
        "post_title": "Green Singapore!",
        "post_description": "Can't wait to land in the greenest of nations, Singapore! Verdex has been helping a lot, but, do you have any recommendations too?",
        "likes": "0",
        "postDateTime": newPostDatetime,
        "users_who_liked": [],
        "tag": "Nature",
        "targetAccountIDOfPostAuthor": userAccID,
        "comments": {},
        "itineraries": {}
    }
    DI.data["forum"][newPostDatetime] = newPost

    ## Create new admin account
    adminAccEmail = request.form.get("adminEmail")
    adminAccPassword = request.form.get("adminPassword")
    adminAccID = Universal.generateUniqueID()
    adminAccResponse = FireAuth.createUser(email=adminAccEmail, password=adminAccPassword)
    if "ERROR" in adminAccResponse:
        Logger.log("DEBUG PRESENTATIONTRANSFORM ERROR: Admin account creation failed. Error: {}".format(adminAccResponse))
        return "Admin account creation failed. Error: {}".format(adminAccResponse)
    
    DI.data["accounts"][adminAccID] = {
        "id": adminAccID,
        "fireAuthID": adminAccResponse["uid"],
        "username": "admin",
        "email": adminAccEmail,
        "password": Encryption.encodeToSHA256(adminAccPassword),
        "idToken": adminAccResponse["idToken"],
        "refreshToken": adminAccResponse["refreshToken"],
        "tokenExpiry": (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat),
        "disabled": False,
        "admin": True,
        "name": "Admin",
        "position": "Verdex Admin",
        "aboutMe": ""
    }

    ## Make sample support query
    supportQueryID = Universal.generateUniqueID()
    time_stamp = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
    if "supportQueries" not in DI.data["admin"]:
        DI.data["admin"]["supportQueries"] = {}

    DI.data["admin"]["supportQueries"][supportQueryID] = {
        "name": 'John Appleseed',
        "email": request.form.get("supportQueryEmail"),
        "message": "I'm having trouble making a post on VerdexTalks. Can you guide me?",
        "supportQueryID": supportQueryID,
        "timestamp": time_stamp
    }

    DI.save()

    ## Reset other services
    AddonsManager.clearConfig()
    Logger.log("DEBUG PRESENTATIONTRANSFORM: AddonsManager cleared.")
    
    with open(Analytics.filePath, "w") as f:
        json.dump(Analytics.sampleMetricsObject, f)
    if os.path.isdir(os.path.join(os.getcwd(), Analytics.reportsFolderPath)):
        shutil.rmtree(Analytics.reportsFolderPath)
    Analytics.setup()
    Logger.log("DEBUG PRESENTATIONTRANSFORM: Analytics reset, including reports directory.")

    if os.path.isdir(os.path.join(os.getcwd(), FolderManager.tldName)):
        shutil.rmtree(os.path.join(os.getcwd(), FolderManager.tldName))
    FolderManager.setup()
    Logger.log("DEBUG PRESENTATIONTRANSFORM: FolderManager reset.")

    Logger.log("DEBUG PRESENTATIONTRANSFORM: Presentation transform success. User account ID: {}, Admin account ID: {}".format(userAccID, adminAccID))

    report = """
Presentation transform successful. Report:<br><br>

The user account is a Google login account. It cannot be signed into via the standard login flow.<br>
<strong>PLEASE WAIT 10 SECONDS BEFORE LOGGING INTO THE USER ACCOUNT. THIS IS DUE TO GOOGLE OAUTH API LIMITATIONS.</strong><br><br>
User account:<br>
- ID: {}<br>
- Username: {}<br>
- Email: {}<br>
- Password: NA (Google OAuth Login)<br>
<br><br><br>
Admin account:<br>
- ID: {}<br>
- Username: {}<br>
- Email: {}<br>
- Password: {}
<br><br><br>
Analytics data reset including reports data. Admin configuration cleared. UserFolders directory cleared.
    """.format(userAccID, "john", userAccEmail, adminAccID, "admin", adminAccEmail, adminAccPassword)
    return report