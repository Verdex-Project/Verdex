from flask import Flask, request, Blueprint, render_template, redirect, url_for
from main import DI, Logger, Universal, FireConn, FireAuth, FireRTDB
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

    return "Firebase reset success. Accounts and database data wiped."