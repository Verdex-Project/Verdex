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

@accountsBP.route('/', methods=['GET', 'POST'])
def upload_file():
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    #Register folder via FolderManager if not registered
    if not FolderManager.checkIfFolderIsRegistered(filename):
                response = FolderManager.registerFolder(filename)
                if response.startswith("ERROR"):
                    Logger.log("ACCOUNTS UPLOAD_FILE ERROR: Failed to register file for account id {}; response: {}".format(targetAccountID, response))
                    flash("Failed to register a folder in the system for your account. Please try again.")
                    return redirect(request.url)

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Check account folder for a previous pfp, if exists, delete
            if (not isinstance(FolderManager.getFilenames(targetAccountID))) and (not FolderManager.getFilenames().startswith("ERROR")):
                try:
                    response = FolderManager.deleteFile(targetAccountID, FolderManager.getFilenames(targetAccountID))
                    if response.startswith("ERROR"):
                        Logger.log("ACCOUNTS UPLOAD_FILE ERROR: Failed to delete existing folder for account id {}".format(targetAccountID))
                        flash("An error occured in uploading your file. Please try again.")
                        return redirect(request.url)
                except Exception as e:
                    Logger.log("ACCOUNTS UPLOAD_FILE ERROR: Failed to delete existing folder for account id {}".format(targetAccountID))
                    flash("An error occured in uploading your file. Please try again.")
                    return redirect(request.url)

            fileExtension = '.' in filename and filename.rsplit('.', 1)[1].lower()

            filename = secure_filename(targetAccountID, "pfp.", fileExtension)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(request.url)
        else:
            flash("File extension not allowed.")
            return redirect(request.url)
    else:
        return render_template('')