import json, random, time, sys, subprocess, os, shutil, copy, requests, datetime
from flask import Flask, request, Blueprint, session, redirect, url_for, send_file, send_from_directory, jsonify
from main import DI, FireAuth, Universal, manageIDToken, deleteSession, Logger
from models import *
from generation.itineraryGeneration import staticLocations
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

@apiBP.route('/api/loginAccount', methods=['POST'])
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
    
    accID = Universal.generateUniqueID()
    DI.data["accounts"][accID] = {
        "id": accID,
        "fireAuthID": tokenInfo["uid"],
        "username": request.json["username"],
        "email": request.json["email"],
        "password": request.json["password"],
        "idToken": tokenInfo['idToken'],
        "refreshToken": tokenInfo['refreshToken'],
        "tokenExpiry": (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat)
    }
    DI.save()

    session["idToken"] = tokenInfo["idToken"]

    return "SUCCESS: Account created successfully"

@apiBP.route("/api/generateItinerary", methods=["POST"])
def generateItinerary():
    headersCheck = checkHeaders(request.headers)
    if headersCheck != True:
        return headersCheck
    
    ## Check body
    if "targetLocations" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    if not isinstance(request.json["targetLocations"], list):
        return "ERROR: One or more required payload parameters are invalid."
    if "title" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    if "description" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    
    ## Generate itinerary object
    newItinerary = {
        "id": Universal.generateUniqueID(),
        "title": request.json["title"].strip(),
        "description": request.json["description"].strip(),
        "generationDatetime": datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat),
        "days": {}
    }

    ## Generate days
    allActivities = request.json["targetLocations"]
    remainingActivities = [x for x in staticLocations if x not in allActivities]

    ### Insert remaining activities into all activities at random indexes
    for activity in remainingActivities:
        allActivities.insert(random.randint(0, len(allActivities)), activity)

    firstDayActivities = allActivities[:6]
    secondDayActivities = allActivities[6:]
    for day in range(1, 3):
        newItinerary["days"][str(day)] = {
            "activities": {}
        }

        for activityIndex in range(len((firstDayActivities if day == 1 else secondDayActivities))):
            newItinerary["days"][str(day)]["activities"][str(activityIndex)] = {
                "name": (firstDayActivities if day == 1 else secondDayActivities)[activityIndex]
            }
    
    ## Save itinerary
    DI.data["itineraries"][newItinerary["id"]] = newItinerary
    DI.save()

    return "SUCCESS: Itinerary ID: {}".format(newItinerary["id"])

@apiBP.route("/api/editUsername", methods = ['POST'])
def editUsername():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]
    
    
    # # Check if the username or email is already in use
    # for accountID in DI.data["accounts"]:
    #     if DI.data["accounts"][accountID]["username"] == request.json["username"]:
    #         return "UERROR: Username is already taken."

    # Update the username in the data
    DI.data["accounts"][targetAccountID]["username"] = request.json["username"]
    DI.save()

    return "SUCCESS: Username updated."

@apiBP.route('/api/logoutIdentity', methods=['POST'])
def logoutIdentity():
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    deleteSession(targetAccountID)
    del session['idToken']

    return "SUCCESS: User logged out."


@apiBP.route('/api/deleteIdentity', methods=['POST'])
def deleteIdentity():
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    ## Delete account from DI
    del DI.data["accounts"][targetAccountID]
    DI.save()
    Logger.log("API DELETEIDENTITY: Deleted account with ID '{}' from DI.".format(targetAccountID))

    response = FireAuth.deleteAccount(session['idToken'])
    if response != True:
        Logger.log("API DELETEIDENTITY: Failed to delete account with ID '{}' from FireAuth; error response: {}".format(targetAccountID, response))
        return "ERROR: Something went wrong. Please try again."
    else:
        Logger.log("API DELETEIDENTITY: Deleted account with ID '{}' from FireAuth.".format(targetAccountID))

    del session['idToken']

    return "SUCCESS: Account deleted successfully."

@apiBP.route('/api/likePost', methods=['POST'])
def like_post():
    # if checkHeaders(request.headers) != True:
    #     return checkHeaders(request.headers)
    
    if 'postId' not in request.json:
        return "ERROR: One or more payload parameters were not provided."

    post_id = request.json['postId']

    if post_id in DI.data["forum"]:
        DI.data["forum"][post_id]["likes"] = str(int(DI.data["forum"][post_id]["likes"]) + 1)
        DI.save()

        return jsonify({'likes': int(DI.data["forum"][post_id]["likes"])})

@apiBP.route('/api/deletePost', methods=['POST'])
def delete_post():
    # if checkHeaders(request.headers) != True:
    #     return checkHeaders(request.headers)
    
    if 'postId' not in request.json:
        return "ERROR: One or more payload parameters were not provided."

    post_id = request.json['postId']

    if post_id in DI.data["forum"]:
        DI.data["forum"].pop(post_id)
        DI.save()
    
    return "SUCCESS: Post was successfully removed from the system."

@apiBP.route('/api/nextDay', methods=['POST'])
def nextDay():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    nextDay = request.json['nextDay']
    dayCountList = []

    for key in DI.data["itineraries"]["days"]:
        dayCountList.append(str(key))
    if str(nextDay) not in dayCountList:
        return "ERROR: You are not directed to the next day!"
    else:
        return "SUCCESS: You are directed to the next day!"
    
@apiBP.route('/api/previousDay', methods=['POST'])
def previousDay():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    previousDay = request.json['previousDay']
    dayCountList = []

    for key in DI.data["itineraries"]["days"]:
        dayCountList.append(str(key))
    if str(previousDay) not in dayCountList:
        return "ERROR: You are not directed to the previous day!"
    else:
        return "SUCCESS: You are directed to the previous day!"

@apiBP.route('/api/deleteComment', methods=['POST'])
def deleteComment():
    # if checkHeaders(request.headers) != True:
    #     return checkHeaders(request.headers)

    if 'postId' not in request.json:
        return "ERROR: One or more payload parameters were not provided."
    if 'commentId' not in request.json:
        return "ERROR: One or more payload parameters were not provided."
    
    post_id = request.json['postId']
    comment_id = request.json['commentId']

    if post_id in DI.data["forum"]:
        del DI.data["forum"][post_id]["comments"][comment_id]
        DI.save()
    
    return "SUCCESS: Comment was successfully removed from the post in the system."
