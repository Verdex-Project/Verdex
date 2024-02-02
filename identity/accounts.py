import os
from flask import Flask, render_template, Blueprint, session, redirect, url_for, request, flash
from flask_cors import CORS
from main import DI, FireAuth, Universal, manageIDToken, Logger, secure_filename, allowed_file, app, FolderManager

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

@accountsBP.route('/account/accountRecovery')
def accountRecovery():
    return render_template('identity/accountRecovery.html')

## MyAccount route
@accountsBP.route("/account/info", methods=['GET', 'POST'])
def myAccount():
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if "idToken" not in session:
        return redirect(url_for('unauthorised', error="Please sign in first."))
    
    # PFP Uploading
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file given.')
            return redirect(request.url)

        file = request.files['file']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No file selected.')
            return redirect(request.url)
    
        if file and allowed_file(file.filename):
            # Register folder via FolderManager if not registered
            if not FolderManager.checkIfFolderIsRegistered(targetAccountID):
                response = FolderManager.registerFolder(targetAccountID)
                if response != True:
                    Logger.log("ACCOUNTS MYACCOUNT UPLOADFILE ERROR: Failed to register folder for account id {}; response: {}".format(targetAccountID, response))
                    flash("Failed to register a folder in the system for your account. Please try again.")
                    return redirect(request.url)
            
            fileNames = FolderManager.getFilenames(targetAccountID)
            for file in fileNames:
                filename = file.split('.')[0]
                if filename.endswith("pfp"):
                    location = os.path.join(os.getcwd(), "UserFolders", targetAccountID, file)
                    os.remove(location)

            fileExtension = FolderManager.getFileExtension(file.filename)

            filename = secure_filename("{}_pfp.{}".format(targetAccountID, fileExtension))
            file.save(os.path.join("UserFolders", targetAccountID, filename))
            Logger.log("ACCOUNTS MYACCOUNT UPLOADFILE: File registered for account id {}".format(targetAccountID))
            return redirect(request.url)
    
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