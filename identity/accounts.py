from flask import Flask, render_template, Blueprint, session, redirect, url_for
from flask_cors import CORS
from models import *

accounts = Blueprint("accountsBP",__name__)

@accounts.route('/account/login')
def login():
    return render_template('identity/login.html')

@accounts.route('/account/signup')
def signUp():
    return render_template('identity/signup.html')


## MyAccount route
@accounts.route("/account/info")
def myAccount():
    if "idToken" not in session:
        return redirect(url_for('unauthorised'), error="Please sign in first.")
    targetAccount = None

    for accountID in DI.data["accounts"]:
        if "idToken" in DI.data["accounts"][accountID] and DI.data["accounts"][accountID] == session["idToken"]:
            targetAccount = DI.data["accounts"][accountID]

    return "Hi, {}".format(targetAccount["email"])