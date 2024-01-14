from main import fileContent
from flask import Flask, Blueprint, request, send_file, send_from_directory

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
    
@assetsBP.route("/assets/profileIcon", methods=["GET"])
def profileIcon():
    return send_file("assets/logos/profileIcon.svg", mimetype="image/svg+xml")

@assetsBP.route("/assets/appleLogin", methods=["GET"])
def appleLogin():
    return send_file("assets/logos/appleLogin.png", mimetype="image/png")   

@assetsBP.route("/assets/appleSignup", methods=["GET"])
def appleSignup():
    return send_file("assets/logos/appleSignup.png", mimetype="image/png")

@assetsBP.route("/assets/copyright")
def copyright():
    return fileContent("assets/copyright.js")

@assetsBP.route("/assets/loginJS")
def loginJS():
    return fileContent("js/login.js", passAPIKey=True)

@assetsBP.route("/assets/signupJS")
def signupJS():
    return fileContent("js/signup.js", passAPIKey=True)

@assetsBP.route("/assets/viewAccountJS")
def viewAccountJS():
    return fileContent("js/viewAccount.js", passAPIKey=True)

@assetsBP.route("/assets/editorJS")
def editorJS():
    return fileContent("js/editorNew.js")

@assetsBP.route("/assets/completionJS")
def completionJS():
    return fileContent("js/completion.js")

@assetsBP.route("/assets/targetLocationsJS")
def itineraryGenerationJS():
    return fileContent("js/targetLocations.js", passAPIKey=True)