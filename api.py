import json, random, time, sys, subprocess, os, shutil, copy, requests, datetime
from flask import Flask, request, Blueprint, session
from flask_cors import CORS
from models import *
from dotenv import load_dotenv
load_dotenv()

apiBP = Blueprint("api", __name__)

def checkHeaders(headers):
    for param in ["Content-Type", "VerdexAPIKey"]:
        if param not in headers:
            return "ERROR: One or more required headers not present."
    if headers["Content-Type"] != "application/json":
        return "ERROR: Wrong Content-Type header."
    if headers["VerdexAPIKey"] != os.environ["API_KEY"]:
        return "ERROR: Invalid API key."

    return True

@apiBP.route('/api/loginAccount', methods = ['POST'])
def loginAccount():

    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    if "password" not in request.json:
        return "ERROR: One or more rquired payload parameters not present."
    if "usernameOrEmail" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    
    targetAccountID = None
    for accountID in DI.data["accounts"]:
        if DI.data["accounts"][accountID]["username"] == request.json["usernameOrEmail"]:
            targetAccountID = accountID
            break
        elif DI.data["accounts"][accountID]["email"] == request.json["usernameOrEmail"]:
            targetAccountID = accountID
            break
    if targetAccountID == None:
        return "UERROR: Account does not exist!"
    
    response = FireAuth.login(email=DI.data["accounts"][targetAccountID]["email"], password=request.json["password"])
    if isinstance(response, str):
        return "UERROR: Incorrect email/username or password. Please try again."
    
    DI.data["accounts"][targetAccountID]["idToken"] = response["idToken"]
    DI.data["accounts"][targetAccountID]["refreshToken"] = response["refreshToken"]
    DI.data["accounts"][targetAccountID]["tokenExpiry"] = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat)
    DI.save()

    session["idToken"] = response["idToken"]

    return "SUCCESS: User logged in succesfully"


@apiBP.route("/api/createAccount", methods = ['POST'])
def createAccount():

    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    if "username" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    if "email" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    if "password" not in request.json:
        return "ERROR: One or more required payload parameters not present."

    # Check if the username or email is already in use
    for accountID in DI.data["accounts"]:
        if DI.data["accounts"][accountID]["username"] == request.json["username"]:
            return "UERROR: Username is already taken."

        if DI.data["accounts"][accountID]["email"] == request.json["email"]:
            return "UERROR: Email is already in use."
        
    # Check if password is min length of 6
    if len(request.json["password"]) < 6:
        return "UERROR: Password must be at least 6 characters long."

    # Create a new account
    tokenInfo = FireAuth.createUser(email=request.json["email"], password=request.json["password"])
    if isinstance(tokenInfo, str):
        return "UERROR: Account already exists."
    
    DI.data["accounts"][Universal.generateUniqueID()] = {
        "username": request.json["username"],
        "email": request.json["email"],
        "password": request.json["password"],
        "idToken": tokenInfo['idToken']
    }
    DI.save()

    session["idToken"] = tokenInfo["idToken"]

    return "SUCCESS: Account created successfully"