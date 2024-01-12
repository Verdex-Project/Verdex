from flask import Flask, render_template, Blueprint, session, redirect, url_for
from flask_cors import CORS
from main import DI, FireAuth, Universal, manageIDToken

accountsBP = Blueprint("accounts",__name__)

@accountsBP.route('/account/login')
def login():
    if "idToken" in session:
        return redirect(url_for('accounts.myAccount'))
    
    return render_template('identity/login.html')

@accountsBP.route('/account/signup')
def signUp():
    if "idToken" in session:
        return redirect(url_for('accounts.myAccount'))
    return render_template('identity/signup.html')

## MyAccount route
@accountsBP.route("/account/info")
def myAccount():
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if "idToken" not in session:
        return redirect(url_for('unauthorised', error="Please sign in first."))
    
    targetAccount = DI.data["accounts"][targetAccountID]
    username = targetAccount["username"]
    email = targetAccount["email"]

    return render_template("identity/viewAccount.html", username=username, email=email)