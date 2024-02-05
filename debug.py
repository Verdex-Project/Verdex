from flask import Flask, request, Blueprint, render_template, redirect, url_for
from main import DI, Logger, Universal, FireConn, FireAuth, FireRTDB, AddonsManager, Analytics, Encryption
import os, sys, json, datetime, copy

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
- FireReset: /debug/[key]/fireReset (Wipes all Firebase data, including Firebase Auth accounts, and reloads DI. Use with caution.)
- Toggle usage lock: /debug/[key]/toggleUsageLock
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