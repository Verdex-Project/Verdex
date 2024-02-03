import os, sys, cachecontrol
import google.auth.transport.requests
from google.oauth2 import id_token
from flask import Flask, render_template, Blueprint, session, redirect, url_for, request
from main import DI, FireAuth, Universal, manageIDToken, Logger, GoogleOAuth

accountsBP = Blueprint("accounts",__name__)

@accountsBP.route('/account/login')
def login():
    if "idToken" in session:
        return redirect(url_for('accounts.myAccount'))
    
    return render_template('identity/login.html')

@accountsBP.route('/account/triggerGoogleSignIn')
def triggerGoogleSignIn():
    if not ("GoogleAuthEnabled" in os.environ and os.environ["GoogleAuthEnabled"] == "True"):
        return redirect(url_for("error", error="Google sign-in is not available at this time. Please try again later."))
    authorisationURL, state = GoogleOAuth.oauthFlow.authorization_url()
    session["state"] = state
    return redirect(authorisationURL)

@accountsBP.route('/account/oauthCallback')
def oauthCallback():
    if not ("GoogleAuthEnabled" in os.environ and os.environ["GoogleAuthEnabled"] == "True"):
        return redirect(url_for("error", error="Google sign-in is not available at this time. Please try again later."))
    elif GoogleOAuth.oauthFlow == None or GoogleOAuth.googleClientID == None:
        Logger.log("ACCOUNTS OAUTHCALLBACK ERROR: Google sign-in callback request rejected as OAuth flow or Google Client ID variable not initialised.")
        return redirect(url_for("error", error="Something went wrong. Please try again."))
    elif "idToken" in session:
        return redirect(url_for("accounts.myAccount"))

    GoogleOAuth.oauthFlow.fetch_token(authorization_response=request.url)

    if "state" not in session:
        return redirect(url_for('login'))
    
    if not session["state"] == request.args["state"]:
        Logger.log("ACCOUNTS OAUTHCALLBACK ERROR: Request state mismatch with session state, request rejected.")
        del session["state"]
        return redirect(url_for("error", "Something went wrong. Please try again."))
    
    credentials = GoogleOAuth.oauthFlow.credentials
    request_session = GoogleOAuth.oauthFlow.authorized_session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials.id_token,
        request=token_request,
        audience=GoogleOAuth.googleClientID
    )

    email = id_info.get("email")
    print(email)
    del session["state"]
    return email

@accountsBP.route('/account/signup')
def signUp():
    if "idToken" in session:
        return redirect(url_for('accounts.myAccount'))
    return render_template('identity/signup.html')

@accountsBP.route('/account/accountRecovery')
def accountRecovery():
    return render_template('identity/accountRecovery.html')

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

    ## Check email verification
    notVerified = False
    accInfo = FireAuth.accountInfo(DI.data["accounts"][targetAccountID]["idToken"])
    if isinstance(accInfo, str):
        Logger.log("ACCOUNTS MYACCOUNT ERROR: Failed to get account info for email verification (will assume email is verified); error: {}".format(accInfo))
        notVerified = True
    else:
        notVerified = not accInfo["emailVerified"]

    return render_template("identity/viewAccount.html", username=username, email=email, emailNotVerified=notVerified)