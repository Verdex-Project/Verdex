from flask import Flask, render_template, Blueprint, session, redirect, url_for
from flask_cors import CORS
from models import *

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
    if "idToken" not in session:
        return redirect(url_for('unauthorised', error="Please sign in first."))
    targetAccount = None

    for accountID in DI.data["accounts"]:
        if "idToken" in DI.data["accounts"][accountID] and DI.data["accounts"][accountID]["idToken"] == session["idToken"]:
            targetAccount = DI.data["accounts"][accountID]

    return "Hi, {}".format(targetAccount["email"])