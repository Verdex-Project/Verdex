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
    check = checkHeaders(request.headers)
    if check != True:
        return check
    if 'postId' not in request.json:
        return "ERROR: One or more payload parameters are missing."

    post_id = request.json['postId']

    if post_id in DI.data["forum"]:
        DI.data["forum"][post_id]["likes"] = str(int(DI.data["forum"][post_id]["likes"]) + 1)
        DI.save()
        return jsonify({'likes': int(DI.data["forum"][post_id]["likes"])})
    elif post_id not in DI.data["forum"]:
        return "ERROR: Post ID not found in system."

@apiBP.route('/api/deletePost', methods=['POST'])
def delete_post():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    if 'postId' not in request.json:
        return "ERROR: One or more payload parameters are missing."

    post_id = request.json['postId']

    if post_id in DI.data["forum"]:
        DI.data["forum"].pop(post_id)
        DI.save()
        return "SUCCESS: Post was successfully removed from the system."
    elif post_id not in DI.data["forum"]:
        return "ERROR: Post ID not found in system."

@apiBP.route('/api/nextDay', methods=['POST'])
def nextDay():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    nextDay = request.json['nextDay']
    itineraryID = request.json['itineraryID']

    if 'nextDay' not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if 'itineraryID' not in request.json:
        return "ERROR: One or more required payload parameters not provided."


    dayCountList = []

    for key in DI.data["itineraries"][itineraryID]["days"]:
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
    itineraryID = request.json['itineraryID']

    if 'previousDay' not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if 'itineraryID' not in request.json:
        return "ERROR: One or more required payload parameters not provided."

    dayCountList = []

    for key in DI.data["itineraries"][itineraryID]["days"]:
        dayCountList.append(str(key))
    if str(previousDay) not in dayCountList:
        return "ERROR: You are not directed to the previous day!"
    else:
        return "SUCCESS: You are directed to the previous day!"

@apiBP.route('/api/deleteComment', methods=['POST'])
def deleteComment():
    check = checkHeaders(request.headers)
    if check != True:
        return check

    if 'postId' not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if 'commentId' not in request.json:
        return "ERROR: One or more payload parameters were not provided."
    
    post_id = request.json['postId']
    comment_id = request.json['commentId']

    if post_id in DI.data["forum"]:
        if comment_id in DI.data["forum"][post_id]["comments"]:
            del DI.data["forum"][post_id]["comments"][comment_id]
            DI.save()
            return "SUCCESS: Comment was successfully removed from the post in the system."
        else:
            return "ERROR: Comment ID not found in system."
    else:
        return "ERROR: Post ID not found in system."

@apiBP.route('/api/submitPost', methods=['POST'])
def submitPost():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    if 'user_names' not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if 'post_title' not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if 'post_description' not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if 'post_tag' not in request.json:
        return "ERROR: One or more payload parameters are missing."
    
    user_names = request.json['user_names']
    post_title = request.json['post_title']
    post_description = request.json['post_description']
    post_tag = request.json['post_tag']

    postDateTime = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
    new_post = {
        "user_names": user_names,
        "post_title": post_title,
        "post_description": post_description,
        "likes": "0",
        "postDateTime": postDateTime,
        "liked_status": False,
        "tag": post_tag,
        "comments": {}
    }

    DI.data["forum"][postDateTime] = new_post
    DI.save()
    return "SUCCESS: Post was successfully submitted to the system."

@apiBP.route('/api/commentPost', methods=['POST'])
def commentPost():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    if "post_id" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "comment_description" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    
    post_id = request.json['post_id']
    comment_description = request.json['comment_description']

    if post_id in DI.data["forum"]:
        if 'comments' not in DI.data["forum"][post_id]:
            DI.data["forum"][post_id]['comments'] = {}
        postDateTime = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
        DI.data["forum"][post_id]['comments'][postDateTime] = comment_description
        DI.save()
        return "SUCCESS: Comment successfully made."
    elif post_id not in DI.data["forum"]:
        return "ERROR: Post ID not found in system."
    
@apiBP.route('/api/editPost', methods=['POST'])
def editPost():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    if "post_id" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "edit_user_names" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "edit_post_title" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "edit_post_description" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "edit_post_tag" not in request.json:
        return "ERROR: One or more payload parameters are missing."

    post_id = request.json['post_id']
    edit_user_names = request.json['edit_user_names']
    edit_post_title = request.json['edit_post_title']
    edit_post_description = request.json['edit_post_description']
    edit_post_tag = request.json['edit_post_tag']

    if post_id in DI.data["forum"]:
        DI.data["forum"][post_id]["user_names"] = edit_user_names
        DI.data["forum"][post_id]["post_title"] = edit_post_title
        DI.data["forum"][post_id]["post_description"] = edit_post_description
        DI.data["forum"][post_id]["tag"] = edit_post_tag
        DI.save()
        return "SUCCESS: Post successfully edited."
    elif post_id not in DI.data["forum"]:
        return "ERROR: Post ID not found in system."

# @apiBP.route("/api/newActivityLocationName", methods = ['POST'])
# def newActivityLocationName():
#     check = checkHeaders(request.headers)
#     if check != True:
#         return check

#     day = request.json["day"]
#     activityId = request.json["activityId"]
    
#     DI.data["itineraries"]["days"][day]["activities"][activityId]["name"] = request.json["newActivityName"]
#     DI.data["itineraries"]["days"][day]["activities"][activityId]["location"] = request.json["newActivityLocation"]
#     DI.save()

#     return "SUCCESS: New activity location and name updated."

@apiBP.route('/api/deleteActivity', methods=['POST'])
def deleteActivity():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    day = request.json["day"]
    itineraryID = request.json['itineraryID']
    activityId = request.json["activityId"]

    if 'day' not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if 'activityId' not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if 'itineraryID' not in request.json:
        return "ERROR: One or more required payload parameters not provided."

    DI.data["itineraries"][itineraryID]["days"][day]["activities"].pop(activityId)
    DI.save()
    
    return "SUCCESS: Activity is deleted."

@apiBP.route('/api/deleteItinerary', methods=['POST'])
def deleteItinerary():
    check = checkHeaders(request.headers)
    if check != True:
        return check

    itineraryID = request.json['itineraryID']

    if 'itineraryID' not in request.json:
        return "ERROR: One or more required payload parameters not provided."

    DI.data["itineraries"][itineraryID] = {}
    DI.save()
    
    return "SUCCESS: Itinerarty is deleted."

# @apiBP.route("/api/newActivityStartEndTime", methods = ['POST'])
# def newActivityStartEndTime():
#     check = checkHeaders(request.headers)
#     if check != True:
#         return check

#     day = request.json["day"]
#     activityId = request.json["activityId"]
    
#     DI.data["itineraries"]["days"][day]["activities"][activityId]["startTime"] = request.json["newActivityStartTime"]
#     DI.data["itineraries"]["days"][day]["activities"][activityId]["endTime"] = request.json["newActivityEndTime"]
#     DI.save()

#     return "SUCCESS: New activity start time and end time updated."

@apiBP.route("/api/editActivityModal", methods = ['POST'])
def editActivityModal():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    itineraryID = request.json['itineraryID']
    day = request.json["dayCount"]
    activityId = request.json["activityId"]
    startTime = request.json["newStartTime"]
    endTime = request.json["newEndTime"]
    location = request.json["newLocation"]
    name = request.json["newName"]
    

    print(request.json)

    if 'itineraryID' not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if "dayCount" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if "activityId" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if "newStartTime" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if "newEndTime" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if "newLocation" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if "newName" not in request.json:
        return "ERROR: One or more required payload parameters not provided."

    dayCountList = []
    activityIdList = []

    for key in DI.data["itineraries"][itineraryID]["days"]:
        dayCountList.append(str(key))
    if str(day) not in dayCountList:
        return "UERROR: Day is not found!"
    
    for key in DI.data["itineraries"][itineraryID]["days"][day]["activities"]:
        activityIdList.append(str(key))
    if str(activityId) not in activityIdList:
        return "UERROR: Activity ID not found!"
    
    if not startTime.isnumeric():
        return "UERROR: Start Time is not a numeric value"

    if not endTime.isnumeric():
        return "UERROR: End Time is not a numeric value"

    if len(startTime) != 4:
        return "UERROR: Start Time Format is not correct"
    else:
        DI.data["itineraries"][itineraryID]["days"][day]["activities"][activityId]["startTime"] = startTime
    
    # timeDiff = int(endTime) - int(startTime)
    if len(endTime) != 4 or int(endTime) <= int(startTime) + 30 :
        return "UERROR: End Time Format is not correct and interval should me more than 30 minutes OR End Time is earlier than Start Time!"
    else:
        DI.data["itineraries"][itineraryID]["days"][day]["activities"][activityId]["endTime"] = endTime

    if len(location) > 10:
        return "UERROR: Activity Location should be less than 10 characters!"
    else:
        DI.data["itineraries"][itineraryID]["days"][day]["activities"][activityId]["location"] = location

    if len(name) > 25:
        return "UERROR: Activity name should be less than 25 characters!"
    else:
        DI.data["itineraries"][itineraryID]["days"][day]["activities"][activityId]["name"] = name

    DI.save()
    return "SUCCESS: Activity edits is saved successfully"
