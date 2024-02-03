import os, sys, cachecontrol, datetime
import google.auth.transport.requests
from google.oauth2 import id_token
from flask import Flask, render_template, Blueprint, session, redirect, url_for, request
from main import DI, FireAuth, Universal, manageIDToken, Logger, GoogleOAuth, Encryption

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

    try:
        GoogleOAuth.oauthFlow.fetch_token(authorization_response=request.url)
    except Exception as e:
        Logger.log("ACCOUNTS OAUTHCALLBACK ERROR: Failed to fetch token from Google OAuth flow; error: {}".format(str(e)))
        return redirect(url_for("error", error="Something went wrong. Please try again."))

    if "state" not in session:
        return redirect(url_for('login'))
    
    if not session["state"] == request.args["state"]:
        Logger.log("ACCOUNTS OAUTHCALLBACK ERROR: Request state mismatch with session state, request rejected.")
        del session["state"]
        return redirect(url_for("error", "Something went wrong. Please try again."))
    
    del session["state"]
    
    try:
        credentials = GoogleOAuth.oauthFlow.credentials
        request_session = GoogleOAuth.oauthFlow.authorized_session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)

        id_info = id_token.verify_oauth2_token(
            id_token=credentials.id_token,
            request=token_request,
            audience=GoogleOAuth.googleClientID
        )
    except Exception as e:
        Logger.log("ACCOUNTS OAUTHCALLBACK ERROR: Failed to verify Google ID token; error: {}".format(str(e)))
        return redirect(url_for("error", "Something went wrong. Please try again."))

    email = id_info.get("email")
    if email == None:
        Logger.log("ACCOUNTS OAUTHCALLBACK ERROR: Email not found in Google ID info, request rejected.")
        return redirect(url_for("error", "Something went wrong. Please try again."))
    
    # Process email and create/login account accordingly
    email = email.lower()

    targetAccountID = None
    ## Check if account exists and carry out automated login
    for accountID in DI.data["accounts"]:
        if DI.data["accounts"][accountID]["email"] == email:
            targetAccountID = accountID

            if "googleLogin" not in DI.data["accounts"][targetAccountID] or DI.data["accounts"][targetAccountID]["googleLogin"] != True:
                return redirect(url_for("unauthorised", error="You did not create your account via Google login. Please sign in using your email and password."))

            response = FireAuth.login(email=email, password="googlelogin")
            if isinstance(response, str):
                Logger.log("ACCOUNTS OAUTHCALLBACK ERROR: Failed to login account via automated Google OAuth login; error: {}".format(response))
                return redirect(url_for("unauthorised", error="Failed to login to your account. Please try again."))
            
            DI.data["accounts"][targetAccountID]["idToken"] = response["idToken"]
            DI.data["accounts"][targetAccountID]["refreshToken"] = response["refreshToken"]
            DI.data["accounts"][targetAccountID]["tokenExpiry"] = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat)
            DI.save()
            session["idToken"] = response["idToken"]

            Logger.log("ACCOUNTS OAUTHCALLBACK: Automated login for Google OAuth login; account ID: {}".format(targetAccountID))
            break

    ## If account does not exist, create account
    if targetAccountID == None:
        tokenInfo = FireAuth.createUser(email=email, password="googlelogin")
        if isinstance(tokenInfo, str):
            Logger.log("ACCOUNTS OAUTHCALLBACK ERROR: Failed to create Firebase Auth account for Google OAuth login; error: {}".format(tokenInfo))
            return redirect(url_for("unauthorised", error="Failed to create your account. Please try again."))
        
        targetAccountID = Universal.generateUniqueID()
        DI.data["accounts"][targetAccountID] = {
            "id": targetAccountID,
            "fireAuthID": tokenInfo["uid"],
            "googleLogin": True,
            "username": "Not Set",
            "email": email,
            "password": Encryption.encodeToSHA256("googlelogin"),
            "idToken": tokenInfo["idToken"],
            "refreshToken": tokenInfo["refreshToken"],
            "tokenExpiry": (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat),
            "disabled": False,
            "admin": False,
            "forumBanned": False,
            "reports": {}
        }
        Logger.log("ACCOUNTS OAUTHCALLBACK: New account created for Google OAuth login; account ID: {}".format(targetAccountID))
        DI.save()

        ## Auto-verify email
        response = FireAuth.updateEmailVerifiedStatus(tokenInfo["uid"], True)
        if response != True:
            Logger.log("ACCOUNTS OAUTHCALLBACK ERROR: Failed to auto-verify email for new account created via Google OAuth login; error: {}".format(response))

        session["idToken"] = tokenInfo["idToken"]

    return redirect(url_for("accounts.myAccount"))

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

    googleLinked = "googleLogin" in targetAccount and targetAccount["googleLogin"] == True

    return render_template("identity/viewAccount.html", username=username, email=email, emailNotVerified=notVerified, googleLinked=googleLinked)