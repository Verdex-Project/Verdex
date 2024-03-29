from main import fileContent, FolderManager, manageIDToken
from flask import Flask, Blueprint, request, send_file, send_from_directory, redirect, url_for

assetsBP = Blueprint('assets', __name__)

@assetsBP.route("/assets/logo", methods=["GET"])
def logo():
    type = request.args.get("type")
    if type == "transparentBlack":
        return send_file("assets/logos/transparentLogoBlack.png", mimetype="image/png")
    elif type == "transparentColour":
        return send_file("assets/logos/transparentLogoColour.png", mimetype="image/png")
    elif type == "transparentWhite":
        return send_file("assets/logos/transparentLogoWhite.png", mimetype="image/png")
    elif type == "icon":
        return send_file("assets/logos/icon.png", mimetype="image/png")
    else:
        return send_file("assets/logos/logoColour.png", mimetype="image/png")
    
@assetsBP.route("/assets/userProfilePicture", methods=["GET"])
def userPFP():
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for('assets.profileIcon'))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    folderRegistered = FolderManager.checkIfFolderIsRegistered(targetAccountID)
    if not folderRegistered:
        return redirect(url_for('assets.profileIcon'))

    storedFilenames = FolderManager.getFilenames(targetAccountID)
    filename = None
    for storedFile in storedFilenames:
        storedFilename = storedFile.split('.')[0]
        if storedFilename.endswith("pfp"):
            filename = storedFile
    
    if filename == None:
        return redirect(url_for('assets.profileIcon'))

    mimetype = 'image/'

    if FolderManager.getFileExtension(filename) == 'jpg' or FolderManager.getFileExtension(filename) == 'jpeg':
        mimetype = mimetype + 'jpeg'
    else:
        mimetype = mimetype + FolderManager.getFileExtension(filename)
        
    return send_file('UserFolders/{}/{}'.format(targetAccountID, filename), mimetype=mimetype)

@assetsBP.route("/assets/profileIcon", methods=["GET"])
def profileIcon():
    return send_file("assets/logos/profileIcon.svg", mimetype="image/svg+xml")

@assetsBP.route("/assets/appleLogin", methods=["GET"])
def appleLogin():
    return send_file("assets/appleLogin.png", mimetype="image/png")   

@assetsBP.route("/assets/appleSignup", methods=["GET"])
def appleSignup():
    return send_file("assets/appleSignup.png", mimetype="image/png")

@assetsBP.route("/assets/copyright")
def copyright():
    return fileContent("assets/copyright.js")

@assetsBP.route("/assets/loginJS")
def loginJS():
    return fileContent("js/login.js", passAPIKey=True)

@assetsBP.route("/assets/signupJS")
def signupJS():
    return fileContent("js/signup.js", passAPIKey=True)

@assetsBP.route("/assets/accountRecoveryJS")
def accountRecovery():
    return fileContent("js/accountRecovery.js", passAPIKey=True)

@assetsBP.route("/assets/viewAccountJS")
def viewAccountJS():
    return fileContent("js/viewAccount.js", passAPIKey=True)

@assetsBP.route("/assets/editorJS")
def editorJS():
    return fileContent("js/editor.js", passAPIKey=True)

@assetsBP.route("/assets/completionJS")
def completionJS():
    return fileContent("js/completion.js")

@assetsBP.route("/assets/targetLocationsJS")
def itineraryGenerationJS():
    return fileContent("js/targetLocations.js", passAPIKey=True)

@assetsBP.route("/assets/forumJS")
def forumJS():
    return fileContent("js/forum.js", passAPIKey=True)

@assetsBP.route("/assets/adminJS")
def adminJS():
    return fileContent("js/admin.js", passAPIKey=True)