import json, random, time, sys, subprocess, os, shutil, copy, requests, datetime, pprint, openai
from flask import Flask, request, Blueprint, session, redirect, url_for, send_file, send_from_directory, jsonify, render_template
from main import DI, FireAuth, Universal, manageIDToken, deleteSession, Logger, Emailer, Encryption, AddonsManager, FireConn, Analytics, FolderManager, getNameAndPosition
from dotenv import load_dotenv
load_dotenv()

apiBP = Blueprint("api", __name__)

openAIClient = None
if "VerdexGPTEnabled" in os.environ and os.environ["VerdexGPTEnabled"] == "True" and "VerdexGPTSecretKey" in os.environ:
    try:
        openAIClient = openai.OpenAI(
            api_key=os.environ["VerdexGPTSecretKey"]
        )
    except Exception as e:
        print("API INITIALISATION ERROR: Failed to initialise OpenAI client; error: {}".format(e))
        print("API: System will continue to run without OpenAI client. VerdexGPT prompts will not be available.")
        Logger.log("API INITIALISATION ERROR: Failed to initialise OpenAI client (non-terminal but GPT will be disabled); error: {}".format(e))

def checkHeaders(headers):
    for param in ["Content-Type", "VerdexAPIKey"]:
        if param not in headers:
            return "ERROR: One or more required headers not present."
    if headers["Content-Type"] != "application/json":
        return "ERROR: Wrong Content-Type header."
    if headers["VerdexAPIKey"] != os.environ["API_KEY"]:
        return "ERROR: Invalid API key."

    return True

@apiBP.route('/api/sendPasswordResetKey', methods=['POST'])
def sendPasswordResetKey():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    if "usernameOrEmail" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    
    ## Check if email / username exists
    usernameOrEmail = request.json["usernameOrEmail"]
    targetAccountID = None
    for accountID in DI.data["accounts"]:
        if DI.data["accounts"][accountID]["email"] == usernameOrEmail:
            targetAccountID = accountID
            break
        elif DI.data["accounts"][accountID]["username"] == usernameOrEmail:
            targetAccountID = accountID
            break
    if targetAccountID == None:
        return "UERROR: Account doesnt exist."
    
    if "googleLogin" in DI.data["accounts"][targetAccountID] and DI.data["accounts"][targetAccountID]["googleLogin"] == True:
        return "UERROR: This account is linked to Google, please reset password via Google instead."
    
    resetKeyTime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    resetKeyValue = Analytics.generateRandomID(customLength=6)
    resetKey = f"{resetKeyTime}_{resetKeyValue}"
    DI.data["accounts"][targetAccountID]["resetKey"] = resetKey
    DI.save()

    altText = f"""
    Dear {DI.data["accounts"][targetAccountID]["username"]},

    We received a request to recover your account. To proceed, please use the following reset key: 
    {resetKeyValue}

    If you did not request this, please ignore this email.

    Kind regards, The Verdex Team
    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY VERDEX. DO NOT REPLY TO THIS EMAIL.
    {Universal.copyright}
    """

    html = render_template(
        "emails/forgetCredentialsEmail.html",
        username = DI.data["accounts"][targetAccountID]["username"],
        resetKey = resetKeyValue,
        copyright = Universal.copyright
    )

    Emailer.sendEmail(DI.data["accounts"][targetAccountID]["email"], "Verdex Account Recovery", altText, html)
    
    return "SUCCESS: Password reset key sent to your email."

@apiBP.route('/api/passwordReset', methods=['POST'])
def passwordReset():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    if "resetKeyValue" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    if "newPassword" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    if "cfmPassword" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    if "usernameOrEmail" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    
    usernameOrEmail = request.json["usernameOrEmail"]
    newPassword = request.json["newPassword"].strip()
    cfmPassword = request.json["cfmPassword"].strip()

    ## Get user targetAccountID using usernameOrEmail
    targetAccountID = None
    for accountID in DI.data["accounts"]:
        if DI.data["accounts"][accountID]["email"] == usernameOrEmail:
            targetAccountID = accountID
            break
        elif DI.data["accounts"][accountID]["username"] == usernameOrEmail:
            targetAccountID = accountID
            break
    if targetAccountID == None:
        return "UERROR: No such account with that email or username."
    
    if "googleLogin" in DI.data["accounts"][targetAccountID] and DI.data["accounts"][targetAccountID]["googleLogin"] == True:
        return "UERROR: This account is linked to Google, please reset password via Google instead."

    ## Expire reset keys
    expiredRequestingAccountsResetKey = False
    for accountID in DI.data["accounts"]:
        if "resetKey" in DI.data["accounts"][accountID]:
            key = DI.data["accounts"][accountID]["resetKey"]
            keySplit = key.split('_')
            keyTimeStr = keySplit[0]
            keyValue = keySplit[1]
            ## Check reset key value is valid
            delta = datetime.datetime.now() - datetime.datetime.strptime(keyTimeStr, "%Y-%m-%dT%H:%M:%S")
            if delta.total_seconds() > 900:
                del DI.data["accounts"][accountID]["resetKey"]
                Logger.log("ACCOUNTS PASSWORDRESET: Deleted expired reset key for account ID {}.".format(accountID))
                if accountID == targetAccountID:
                    expiredRequestingAccountsResetKey = True
    
    if expiredRequestingAccountsResetKey:
        return "UERROR: Reset key has expired. Please refresh and try again."

    ## Check if reset key value is correct
    if "resetKey" not in DI.data["accounts"][targetAccountID]:
        return "UERROR: Please request a password reset key first."
    if request.json["resetKeyValue"] != DI.data["accounts"][targetAccountID]["resetKey"].split("_")[1]:
        return "UERROR: Incorrect reset key."

    ## Password validation
    if newPassword != cfmPassword:
        return "UERROR: New and confirm password fields do not match."
    if len(newPassword) < 6:
        return "UERROR: Password must be at least 6 characters long."

    ## Update password
    fireAuthID = DI.data["accounts"][targetAccountID]["fireAuthID"]
    response = FireAuth.updatePassword(fireAuthID=fireAuthID, newPassword=newPassword)
    if response != True:
        Logger.log("ACCOUNTS CHANGEPASSWORD ERROR: Failed to change password; response: {}".format(response))
        return "ERROR: Failed to change password."
    
    ### Update DI
    DI.data["accounts"][targetAccountID]["password"] = Encryption.encodeToSHA256(newPassword)
    del DI.data["accounts"][targetAccountID]["resetKey"]
    DI.save()

    Logger.log("ACCOUNTS PASSWORDRESET: Password reset for account ID {} successful.".format(targetAccountID))
    return "SUCCESS: Password has been reset."

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
    
    if "googleLogin" in DI.data["accounts"][targetAccountID] and DI.data["accounts"][targetAccountID]["googleLogin"] == True:
        return "UERROR: This account is linked to Google, please login via Google instead."
    
    response = FireAuth.login(email=DI.data["accounts"][targetAccountID]["email"], password=request.json["password"])
    if isinstance(response, str):
        return "UERROR: Incorrect email/username or password. Please try again."
    
    DI.data["accounts"][targetAccountID]["idToken"] = response["idToken"]
    DI.data["accounts"][targetAccountID]["refreshToken"] = response["refreshToken"]
    DI.data["accounts"][targetAccountID]["tokenExpiry"] = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat)
    DI.save()

    session["idToken"] = response["idToken"]
    if "admin" in DI.data["accounts"][targetAccountID] and DI.data["accounts"][targetAccountID]["admin"] == True:
        session["admin"] = True

    Analytics.add_metrics(Analytics.EventTypes.sign_in)

    if "generatedItineraryID" in session:
        if session["generatedItineraryID"] in DI.data["itineraries"]:
            if "admin" in session and session["admin"] == True:
                ## Admin accounts cannot be associated with itineraries
                del DI.data["itineraries"][session["generatedItineraryID"]]
                DI.save()
                del session["generatedItineraryID"]
            else:
                ## Link itinerary to account
                DI.data["itineraries"][session["generatedItineraryID"]]["associatedAccountID"] = targetAccountID
                DI.save()
            
                generatedItineraryID = session["generatedItineraryID"]
                del session["generatedItineraryID"]
                return "SUCCESS ITINERARYREDIRECT: User logged in succesfully. Itinerary ID: {}".format(generatedItineraryID)
        else:
            ## Invalid itinerary ID
            del session["generatedItineraryID"]

    return "SUCCESS: User logged in succesfully."

@apiBP.route("/api/createAccount", methods = ['POST'])
def createAccount():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    if "username" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    if not isinstance(request.json["username"], str):
        return "ERROR: Invalid username provided."
    if not request.json["username"].isalnum():
        return "UERROR: Username can only contain alphanumeric characters."
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
        Logger.log("ACCOUNTS CREATEACCOUNT ERROR: Account creation failed; response: {}".format(tokenInfo))
        return "UERROR: Please enter a valid Email."
    
    accID = Universal.generateUniqueID()
    DI.data["accounts"][accID] = {
        "id": accID,
        "fireAuthID": tokenInfo["uid"],
        "googleLogin": False,
        "username": request.json["username"],
        "email": request.json["email"],
        "password": Encryption.encodeToSHA256(request.json["password"]),
        "idToken": tokenInfo['idToken'],
        "refreshToken": tokenInfo['refreshToken'],
        "tokenExpiry": (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat),
        "disabled": False,
        "admin": False,
        "forumBanned": False,
        "aboutMe": "",
        "reports": {}
    }
    Logger.log("Account with ID {} created.".format(accID))
    DI.save()

    verifyEmailLink = FireAuth.generateEmailVerificationLink(request.json["email"])
    if verifyEmailLink.startswith("ERROR"):
        Logger.log("ACCOUNTS CREATEACCOUNT ERROR: Failed to generate email verification link; response: {}".format(verifyEmailLink))
        return "ERROR: Email verification link generation failed."

    altText = f"""
    Dear {request.json["username"]},
    
    Thank you for Thank you for signing up with Verdex! To finish signing up, please verify your email here:
    {verifyEmailLink}

    If you did not request this, please ignore this email.

    Kind regards, The Verdex Team
    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY VERDEX. DO NOT REPLY TO THIS EMAIL.
    {Universal.copyright}
    """

    html = render_template(
        "emails/createAccountEmail.html",
        username = request.json["username"],
        verifyEmailLink = verifyEmailLink,
        copyright = Universal.copyright
    )

    Emailer.sendEmail(request.json["email"], "Welcome To Verdex", altText, html)
    # destEmail, subject, altText, html

    session["idToken"] = tokenInfo["idToken"]
    if "generatedItineraryID" in session:
        if session["generatedItineraryID"] in DI.data["itineraries"]:
            DI.data["itineraries"][session["generatedItineraryID"]]["associatedAccountID"] = accID
            DI.save()
            
            generatedItineraryID = session["generatedItineraryID"]
            del session["generatedItineraryID"]
            return "SUCCESS ITINERARYREDIRECT: Account created successfully. Itinerary ID: {}".format(generatedItineraryID)
        del session["generatedItineraryID"]

    return "SUCCESS: Account created successfully."

@apiBP.route("/api/generateItinerary", methods=["POST"])
def generateItinerary():
    headersCheck = checkHeaders(request.headers)
    if headersCheck != True:
        return headersCheck
    
    authCheck = manageIDToken()
    targetAccountID = None
    if authCheck.startswith("SUCCESS"):
        targetAccountID = authCheck[len("SUCCESS: ")::]
    
    # Check body
    if "targetLocations" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    if not isinstance(request.json["targetLocations"], list):
        return "ERROR: One or more required payload parameters are invalid."
    if "title" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    if "description" not in request.json:
        return "ERROR: One or more required payload parameters not present."
    
    if len(Universal.generationData) == 0 or 'locations' not in Universal.generationData or len(Universal.generationData['locations']) == 0:
        return "UERROR: Generation data not available. Please try again later."

    cleanTargetLocations = [x for x in request.json['targetLocations'] if x in Universal.generationData['locations']]
    if len(cleanTargetLocations) > 9:
        cleanTargetLocations = cleanTargetLocations[:9]
    
    uniqueLocations = []
    for location in cleanTargetLocations:
        if location not in uniqueLocations:
            uniqueLocations.append(location)
    cleanTargetLocations = uniqueLocations

    title: str = request.json['title'].strip()
    description: str = request.json['description'].strip()
    
    # Itinerary generation process
    firstActivityTimeRange = ("0900", "1200")
    secondActivityTimeRange = ("1300", "1600")
    thirdActivityTimeRange = ("1600", "1800")
    activityTimeRanges = [firstActivityTimeRange, secondActivityTimeRange, thirdActivityTimeRange]

    ## Prepare root itinerary object
    itineraryID = Universal.generateUniqueID()
    itinerary = {
        "title": title,
        "description": description,
        "associatedAccountID": "None" if targetAccountID == None else targetAccountID,
        "generationDatetime": datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat),
        "days": {}
    }

    ## Prepare locations list
    locations = cleanTargetLocations
    duplicatesInsertedAsContingency = 0
    while len(locations) < 9:
        randomIndex = random.randint(0, len(locations) - 1) if len(locations) > 0 else 0
        randomLocation = None
        attempts = 30
        while (randomLocation == None or randomLocation in locations) and attempts > 0:
            randomLocation = random.choice([name for name in Universal.generationData["locations"]])
            attempts -= 1
        
        ## If a unique new location really cannot be found, insert a random location, regardless of duplicates
        if randomLocation == None or attempts <= 0:
            locations.insert(randomIndex, random.choice([name for name in Universal.generationData["locations"]]))
            duplicatesInsertedAsContingency += 1
            continue

        locations.insert(randomIndex, randomLocation)
    
    if duplicatesInsertedAsContingency > 0:
        Logger.log("API GENERATEITINERARY WARNING: {} duplicate locations inserted as contingency as enough new unique locations could not be found to insert.".format(duplicatesInsertedAsContingency))
    
    activities = [tuple(locations[i:i+3]) for i in range(0, len(locations), 3)]

    ## Prepare days
    sevenDayDeltaObject = datetime.datetime.now() + datetime.timedelta(days=7)
    dayDates = [(sevenDayDeltaObject + datetime.timedelta(days=i+1)).strftime("%Y-%m-%d") for i in range(3)]

    ## Generate days
    for dayCount in range(3):
        day = {
            "date": dayDates[dayCount],
            "activities": {}
        }

        for activityCount in range(3):
            activityLocation = activities[dayCount][activityCount]

            attempts = 5
            activityType = None
            while (activityType == None or activityType in [x["activity"] for x in day["activities"].values()]) and attempts > 0:
                activityType = random.choice(Universal.generationData["locations"][activityLocation]["supportedActivities"])
                attempts -= 1
            
            if activityType == None:
                ## Backup default activity type
                activityType = "Visiting"
            
            startTime = activityTimeRanges[activityCount][0]
            endTime = activityTimeRanges[activityCount][1]
            
            day["activities"][str(activityCount)] = {
                "name": activities[dayCount][activityCount],
                "activity": activityType,
                "imageURL": Universal.generationData["locations"][activityLocation]["imageURL"],
                "startTime": startTime,
                "endTime": endTime
            }

        itinerary["days"][str(dayCount + 1)] = day
    
    ## Save itinerary
    DI.data["itineraries"][itineraryID] = itinerary
    DI.save()

    if targetAccountID == None:
        ## Triggers redirect to create account/login flow
        session["generatedItineraryID"] = itineraryID

        return "SUCCESS ACCOUNTREDIRECT: Itinerary ID: {}".format(itineraryID)
    else:
        return "SUCCESS: Itinerary ID: {}".format(itineraryID)

@apiBP.route("/api/editUsername", methods = ['POST'])
def editUsername():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]
    
    ## Check body
    if "username" not in request.json:
        return "ERROR: One or more payload not present."
    if not isinstance(request.json["username"], str):
        return "ERROR: Invalid username provided."
    if not request.json["username"].isalnum():
        return "UERROR: Username can only contain alphanumeric characters."
    
    # Check if the username is already in use
    for accountID in DI.data["accounts"]:
        if DI.data["accounts"][accountID]["username"] == request.json["username"]:
            return "UERROR: Username is already taken."

    # Update the username in the data
    DI.data["accounts"][targetAccountID]["username"] = request.json["username"]
    DI.save()

    return "SUCCESS: Username updated."

@apiBP.route("/api/editEmail", methods = ['POST'])
def editEmail():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    ## Check body
    if "email" not in request.json:
        return "ERROR: One or more payload not present."
    for accountID in DI.data["accounts"]:
        if DI.data["accounts"][accountID]["email"] == request.json["email"]:
            return "UERROR: Email is already taken."
        
    if "googleLogin" in DI.data["accounts"][targetAccountID] and DI.data["accounts"][targetAccountID]["googleLogin"] == True:
        return "UERROR: This account is linked to Google, email cannot be changed."
    
    # Success case
        
    ## Change email in Firebase Authentication
    response = FireAuth.changeUserEmail(fireAuthID = DI.data["accounts"][targetAccountID]["fireAuthID"], newEmail = request.json["email"])
    if response != True:
        Logger.log("API EDITEMAIL ERROR: Failed to get FireAuth to change email for account ID '{}'; response: {}".format(targetAccountID, response))
        return "ERROR: Failed to change email."
    
    ## Change email verified status to False in Firebase Authentication (ignore if goes wrong)
    verification = FireAuth.updateEmailVerifiedStatus(DI.data["accounts"][targetAccountID]["fireAuthID"], False)
    if verification != True:
        Logger.log("ACCOUNTS EDITEMAIL ERROR: Failed to update email verification status; response: {}".format(response))

    ## Generate email verification link
    username = DI.data["accounts"][targetAccountID]["username"]
    email = request.json["email"]
    verifyEmailLink = FireAuth.generateEmailVerificationLink(email)
    if verifyEmailLink.startswith("ERROR"):
        Logger.log("ACCOUNTS EDITEMAIL ERROR: Failed to generate email verification link; response: {}".format(response))
        return "ERROR: Email verification link generation failed."
    
    ## Nullify session
    deleteSession(targetAccountID)

    altText = f"""
    Dear {username},
    
    Please verify your email here:
    {verifyEmailLink}

    If you did not request this, please ignore this email.

    Kind regards, The Verdex Team
    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY VERDEX. DO NOT REPLY TO THIS EMAIL.
    {Universal.copyright}
    """

    html = render_template(
        "emails/resendVerificationEmail.html",
        username = username,
        verifyEmailLink = verifyEmailLink,
        copyright = Universal.copyright
    )

    ## Dispatch email with link via Emailer
    Emailer.sendEmail(email, "Verdex Email Verification", altText, html)

    # Update the email in the data
    DI.data["accounts"][targetAccountID]["email"] = request.json["email"]
    DI.save()
    
    return "SUCCESS: Email updated and verification sent! Please re-login."

@apiBP.route('/api/resendEmail', methods=['POST'])
def resendEmail():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if "googleLogin" in DI.data["accounts"][targetAccountID] and DI.data["accounts"][targetAccountID]["googleLogin"] == True:
        return "UERROR: This account is linked to Google, email verification is not needed."

    token = DI.data["accounts"][targetAccountID]["idToken"]
    verified = FireAuth.accountInfo(token)["emailVerified"]
    if verified != False:
        return "ERROR: Email already verified!"

    username = DI.data["accounts"][targetAccountID]["username"]
    email = DI.data["accounts"][targetAccountID]["email"]
    verifyEmailLink = FireAuth.generateEmailVerificationLink(email)
    if verifyEmailLink.startswith("ERROR"):
        Logger.log("ACCOUNTS EDITEMAIL ERROR: Failed to generate email verification link; response: {}".format(verifyEmailLink))
        return "ERROR: Email verification link generation failed."

    altText = f"""
    Dear {username},
    
    Please verify your email here:
    {verifyEmailLink}

    If you did not request this, please ignore this email.

    Kind regards, The Verdex Team
    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY VERDEX. DO NOT REPLY TO THIS EMAIL.
    {Universal.copyright}
    """

    html = render_template(
        "emails/resendVerificationEmail.html",
        username = username,
        verifyEmailLink = verifyEmailLink,
        copyright = Universal.copyright
    )

    Emailer.sendEmail(email, "Verdex Email Verification", altText, html)
    return "SUCCESS: Email verification sent."

@apiBP.route('/api/changePassword', methods=['POST'])
def changePassword():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    ## Check body
    if "currentPassword" not in request.json:
        return "ERROR: One or more payload not present."
    if "newPassword" not in request.json:
        return "ERROR: One or more payload not present."
    if "cfmNewPassword" not in request.json:
        return "ERROR: One or more payload not present."
    
    currentPassword = request.json["currentPassword"].strip()
    newPassword = request.json["newPassword"].strip()
    cfmNewPassword = request.json["cfmNewPassword"].strip()
    
    if newPassword != cfmNewPassword:
        return "UERROR: New and confirm password fields do not match."
    if len(newPassword) < 6:
        return "UERROR: Password must be at least 6 characters long."
    if currentPassword == newPassword:
        return "UERROR: New password must differ from the current password."
    
    if "googleLogin" in DI.data["accounts"][targetAccountID] and DI.data["accounts"][targetAccountID]["googleLogin"] == True:
        return "UERROR: This account is linked to Google, please change password via Google instead."
    
    ## Return change password cannot be executed if current password is not stored (in case of database synchronisation problems)
    if "password" not in DI.data["accounts"][targetAccountID]:
        return "UERROR: Your password cannot be changed at this time. Please try again."
    
    ## Check if current password is correct
    oldPassword = DI.data["accounts"][targetAccountID]["password"]
    if not Encryption.verifySHA256(currentPassword, oldPassword):
        return "UERROR: Current password is incorrect."

    ## Update password
    fireAuthID = DI.data["accounts"][targetAccountID]["fireAuthID"]
    response = FireAuth.updatePassword(fireAuthID=fireAuthID, newPassword=newPassword)
    if response != True:
        Logger.log("ACCOUNTS CHANGEPASSWORD ERROR: Failed to change password; response: {}".format(response))
        return "ERROR: Failed to change password."
    
    ### Update DI
    DI.data["accounts"][targetAccountID]["password"] = Encryption.encodeToSHA256(newPassword)
    DI.save()
    
    ## Automated re-login
    email = DI.data["accounts"][targetAccountID]["email"]
    loginResponse = FireAuth.login(email=email, password=newPassword)
    if isinstance(loginResponse, str) and loginResponse.startswith("ERROR"):
        Logger.log("ACCOUNTS CHANGEPASWORD ERROR: Auto login failed; response: {}".format(loginResponse))
        deleteSession(targetAccountID)
        return "ERROR: Change password auto login failed."
    else:
        DI.data["accounts"][targetAccountID]["idToken"] = loginResponse["idToken"]
        DI.data["accounts"][targetAccountID]["refreshToken"] = loginResponse["refreshToken"]
        DI.data["accounts"][targetAccountID]["tokenExpiry"] = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat)
        DI.save()
        session["idToken"] = loginResponse["idToken"]
    
    return "SUCCESS: Password updated successfully."

@apiBP.route('/api/deletePFP', methods=['POST'])
def deletePFP():
    check = checkHeaders(request.headers)
    if check != True:
        return check

    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    folderRegistered = FolderManager.checkIfFolderIsRegistered(targetAccountID)
    if not folderRegistered:
        return "ERROR: No folder registered."

    storedFilenames = FolderManager.getFilenames(targetAccountID)
    for storedFile in storedFilenames:
        storedFilename = storedFile.split('.')[0]
        if storedFilename.endswith("pfp"):
            location = os.path.join(os.getcwd(), "UserFolders", targetAccountID, storedFile)
            os.remove(location)

    Logger.log("ACCOUNTS DELETEPFP: Profile picture deleted for {}".format(targetAccountID))

    return "SUCCESS: File removed successfully."

@apiBP.route('/api/editAboutMeDescription', methods=['POST'])
def aboutMeDescription():
    check = checkHeaders(request.headers)
    if check != True:
        return check

    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if "description" not in request.json:
        return "ERROR: One or more payload not present."
    
    if not isinstance(request.json["description"], str):
        return "ERROR: Invalid description provided."
    
    description = request.json["description"].strip()
    
    if len(description) > 150:
        return "UERROR: Your description cannot exceed 150 characters."

    DI.data["accounts"][targetAccountID]["aboutMe"] = description
    Logger.log("ACCOUNTS ABOUTMEDESCRIPTION: About Me description updated for {}".format(targetAccountID))
    DI.save()

    return "SUCCESS: Description updated."

@apiBP.route('/api/logoutIdentity', methods=['POST'])
def logoutIdentity():
    check = checkHeaders(request.headers)
    if check != True:
        return check

    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]
    
    deleteSession(targetAccountID)

    Analytics.add_metrics(Analytics.EventTypes.sign_out)

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
    
    response = FireAuth.deleteAccount(session['idToken'])
    if response != True:
        Logger.log("API DELETEIDENTITY ERROR: Failed to delete account with ID '{}' from FireAuth; error response: {}".format(targetAccountID, response))
        return "ERROR: Something went wrong. Please try again."
    else:
        Logger.log("API DELETEIDENTITY: Deleted account with ID '{}' from FireAuth.".format(targetAccountID))
    
    ## Delete account and account-generated resources from DI
    del DI.data["accounts"][targetAccountID]

    ### Delete itineraries
    for itineraryID in copy.deepcopy(DI.data["itineraries"]):
        if "associatedAccountID" in DI.data["itineraries"][itineraryID] and DI.data["itineraries"][itineraryID]["associatedAccountID"] == targetAccountID:
            del DI.data["itineraries"][itineraryID]

    ### Delete posts
    for postDatetime in copy.deepcopy(DI.data["forum"]):
        if DI.data["forum"][postDatetime]["targetAccountIDOfPostAuthor"] == targetAccountID:
            del DI.data["forum"][postDatetime]

    DI.save()

    ## Remove the userfolder
    if FolderManager.checkIfFolderIsRegistered(targetAccountID):
        FolderManager.deleteFolder(targetAccountID)

    Logger.log("API DELETEIDENTITY: Deleted account with ID '{}' from DI.".format(targetAccountID))

    session.clear()

    return "SUCCESS: Account deleted successfully."

@apiBP.route('/api/likePost', methods=['POST'])
def like_post():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if 'postId' not in request.json:
        return "ERROR: One or more payload parameters are missing."

    post_id = request.json['postId']

    if post_id in DI.data["forum"]:
        if targetAccountID not in DI.data["forum"][post_id]["users_who_liked"]:
            DI.data["forum"][post_id]["likes"] = str(int(DI.data["forum"][post_id]["likes"]) + 1)
            DI.data["forum"][post_id]["users_who_liked"].append(targetAccountID)
            DI.save()
            return jsonify({'likes': int(DI.data["forum"][post_id]["likes"])})
        else:
            DI.data["forum"][post_id]["likes"] = str(int(DI.data["forum"][post_id]["likes"]) - 1)
            DI.data["forum"][post_id]["users_who_liked"].remove(targetAccountID)
            DI.save()
            return jsonify({'likes': int(DI.data["forum"][post_id]["likes"])})
        
    return "ERROR: Post ID not found in system."

@apiBP.route('/api/deletePost', methods=['POST'])
def delete_post():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]
    
    if 'postId' not in request.json:
        return "ERROR: One or more payload parameters are missing."

    post_id = request.json['postId']

    if post_id in DI.data["forum"]:
        if targetAccountID == DI.data["forum"][post_id]["targetAccountIDOfPostAuthor"]:
            del DI.data["forum"][post_id]
            DI.save()
            return "SUCCESS: Post was successfully removed from the system."
        else:
            return "UERROR: You can't delete someone else's post!"
    
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
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if 'postId' not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if 'commentId' not in request.json:
        return "ERROR: One or more payload parameters were not provided."
    
    post_id = request.json['postId']
    comment_id = request.json['commentId']

    if post_id in DI.data["forum"]:
        if comment_id in DI.data["forum"][post_id]["comments"]:
            if targetAccountID == DI.data["forum"][post_id]["targetAccountIDOfPostAuthor"] or targetAccountID == comment_id.split("_")[1]:
                del DI.data["forum"][post_id]["comments"][comment_id]
                DI.save()
                return "SUCCESS: Comment was successfully removed from the post in the system."
            else:
                return "UERROR: You can't delete someone else's comment!"
        else:
            return "ERROR: Comment ID not found in system."
    else:
        return "ERROR: Post ID not found in system."

@apiBP.route('/api/submitPost', methods=['POST'])
def submitPost():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]
    
    if 'post_title' not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if 'post_description' not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if 'post_tag' not in request.json:
        return "ERROR: One or more payload parameters are missing."
    
    post_title = request.json['post_title']
    post_description = request.json['post_description']
    post_tag = request.json['post_tag']

    postDateTime = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
    new_post = {
        "username": DI.data["accounts"][targetAccountID]["username"],
        "post_title": post_title,
        "post_description": post_description,
        "likes": "0",
        "postDateTime": postDateTime,
        "users_who_liked": [],
        "tag": post_tag,
        "targetAccountIDOfPostAuthor": targetAccountID,
        "comments": {},
        "itineraries": {}
    }

    DI.data["forum"][postDateTime] = new_post
    DI.save()

    Analytics.add_metrics(Analytics.EventTypes.forumPost)
    print(Analytics.data)

    return "SUCCESS: Post was successfully submitted to the system."

@apiBP.route('/api/commentPost', methods=['POST'])
def commentPost():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]
    
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
        DI.data["forum"][post_id]['comments'][str(postDateTime + "_" + targetAccountID + "_" + DI.data["accounts"][targetAccountID]["username"])] = comment_description
        DI.save()
        return "SUCCESS: Comment successfully made."
    else:
        return "ERROR: Post ID not found in system."
      
@apiBP.route('/api/editPost', methods=['POST'])
def editPost():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]
    
    if "post_id" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "edit_post_title" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "edit_post_description" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "edit_post_tag" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    
    post_id = request.json['post_id']
    edit_post_title = request.json['edit_post_title']
    edit_post_description = request.json['edit_post_description']
    edit_post_tag = request.json['edit_post_tag']

    if targetAccountID == DI.data["forum"][post_id]["targetAccountIDOfPostAuthor"]:
        if post_id in DI.data["forum"]:
            DI.data["forum"][post_id]["post_title"] = edit_post_title
            DI.data["forum"][post_id]["post_description"] = edit_post_description
            DI.data["forum"][post_id]["tag"] = edit_post_tag
            DI.save()
            return "SUCCESS: Post successfully edited."
        else:
            return "ERROR: Post ID not found in system."
    else:
        return "UERROR: You can't edit someone else's post!"

@apiBP.route('/api/openEditPost', methods=['POST'])
def openEditPost():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if "post_id" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    
    post_id = request.json['post_id']

    if targetAccountID != DI.data["forum"][post_id]["targetAccountIDOfPostAuthor"]:
        return "UERROR: You can't edit someone else's post!"
    
    return "SUCCESS: Post successfully opened for editing."

@apiBP.route('/api/submitPostWithItinerary', methods=['POST'])
def submitPostWithItinerary():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]
    
    if "itinerary_post_title" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "itinerary_post_description" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "itinerary_post_tag" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "itinerary_id" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "itinerary_title" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "itinerary_description" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    
    itinerary_post_title = request.json['itinerary_post_title']
    itinerary_post_description = request.json['itinerary_post_description']
    itinerary_post_tag = request.json['itinerary_post_tag']
    itinerary_id = request.json['itinerary_id']
    itinerary_title = request.json['itinerary_title']
    itinerary_description = request.json['itinerary_description']

    postDateTime = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
    new_post = {
        "username": DI.data["accounts"][targetAccountID]["username"],
        "post_title": itinerary_post_title,
        "post_description": itinerary_post_description,
        "likes": "0",
        "postDateTime": postDateTime,
        "users_who_liked": [],
        "tag": itinerary_post_tag,
        "targetAccountIDOfPostAuthor": targetAccountID,
        "comments": {},
        "itineraries": {
            itinerary_id: {
                "itinerary_title": itinerary_title,
                "itinerary_description": itinerary_description
            }
        }
    }
    DI.data["forum"][postDateTime] = new_post
    DI.save()

    Analytics.add_metrics(Analytics.EventTypes.forumPost)
    print(Analytics.data)

    return "SUCCESS: Itinerary was successfully shared to the forum."

@apiBP.route('/api/submitReport', methods=['POST'])
def submitReport():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if "author_acc_id" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "report_reason" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    
    author_acc_id = request.json['author_acc_id']
    report_reason = request.json['report_reason']

    postDateTime = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)

    if author_acc_id in DI.data["accounts"]:
        if targetAccountID != author_acc_id:
            if "reports" not in DI.data["accounts"][author_acc_id]:
                DI.data["accounts"][author_acc_id]["reports"] = {}
            DI.data["accounts"][author_acc_id]["reports"][str(targetAccountID + "_" + postDateTime)] = report_reason
            DI.save()
            return "SUCCESS: Report was successfully submitted to the system."
        else:
            return "UERROR: You can't report yourself!"
    else:
        return "ERROR: User account ID not found in system."



@apiBP.route("/api/editActivity", methods = ['POST'])
def editActivity():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    itineraryID = request.json['itineraryID']
    day = request.json["dayCount"]
    activityId = request.json["activityId"]
    startTime = request.json["newStartTime"]
    endTime = request.json["newEndTime"]
    activity = request.json["newActivity"]
    name = request.json["newName"]

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
    if "newActivity" not in request.json:
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

    if len(startTime) != 4 or int(startTime[0:2]) >= 24 or int(startTime[2:]) >= 60 :
        return "UERROR: Start Time Format is not correct"
    else:
        DI.data["itineraries"][itineraryID]["days"][day]["activities"][activityId]["startTime"] = startTime
    
    timeDiff = int(endTime) - int(startTime)
    if len(endTime) != 4 or int(endTime) < int(startTime) or timeDiff < 30  or int(endTime[0:2]) >= 24  or int(endTime[2:]) >= 60 :
        return "UERROR: End Time Format is not correct and should be 30 minutes earlier than Start Time!"
    else:
        DI.data["itineraries"][itineraryID]["days"][day]["activities"][activityId]["endTime"] = endTime

    if len(activity) > 10:
        return "UERROR: Activity should be less than 10 characters!"
    else:
        DI.data["itineraries"][itineraryID]["days"][day]["activities"][activityId]["activity"] = activity

    if len(name) > 40:
        return "UERROR: Activity name should be less than 40 characters!"
    else:
        DI.data["itineraries"][itineraryID]["days"][day]["activities"][activityId]["name"] = name

    DI.save()
    return "SUCCESS: Activity edits is saved successfully"

@apiBP.route("/api/addNewActivity", methods = ['POST'])
def addNewActivity():
    check = checkHeaders(request.headers)
    if check != True:
        return check

    if False in [(requiredParameter in request.json) for requiredParameter in ["itineraryID","dayCount","currentStartTime","currentEndTime","currentImageURL","currentActivity","currentName","newActivityID"]]:
        return "ERROR: One or more payload parameters are not provided."
    
    itineraryID = request.json['itineraryID']
    day = request.json["dayCount"]
    startTime = request.json["currentStartTime"]
    endTime = request.json["currentEndTime"]
    imageURL = request.json["currentImageURL"]
    activity = request.json["currentActivity"]
    name = request.json["currentName"]
    newActivityId = str(request.json["newActivityID"])

    dayCountList = []
    activityIdList = []

    for key in DI.data["itineraries"][itineraryID]["days"]:
        dayCountList.append(str(key))
    if str(day) not in dayCountList:
        return "UERROR: Day is not found!"
    
    for key in DI.data["itineraries"][itineraryID]["days"][day]["activities"]:
        activityIdList.append(str(key))

    DI.data["itineraries"][itineraryID]["days"][day]["activities"][newActivityId] = {"startTime" : startTime, "endTime" : endTime, "imageURL": imageURL, "activity" : activity, "name" : name}
    DI.save()

    return "SUCCESS: New activity is added successfully"

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

    activityData = [DI.data["itineraries"][itineraryID]["days"][day]["activities"][id] for id in DI.data["itineraries"][itineraryID]["days"][day]["activities"]]
    newActivitiesData = {}
    for index in range(len(activityData)):
        newActivitiesData[str(index)] = activityData[index]
    
    DI.data["itineraries"][itineraryID]["days"][day]["activities"] = newActivitiesData

    DI.save()
    
    return "SUCCESS: Activity is deleted."

@apiBP.route('/api/deleteItinerary', methods=['POST'])
def deleteItinerary():
    check = checkHeaders(request.headers)
    if check != True:
        return check

    if 'itineraryID' not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if request.json["itineraryID"] not in DI.data["itineraries"]:
        return "ERROR: Itinerary ID not found."

    itineraryID = request.json['itineraryID']

    del DI.data["itineraries"][itineraryID]
    DI.save()
    
    return "SUCCESS: Itinerary is deleted."

@apiBP.route('/api/sendTestEmail', methods=['POST'])
def sendTestEmail():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    authCheck = manageIDToken(checkIfAdmin=True)
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    username = DI.data["accounts"][targetAccountID]["username"]
    email = DI.data["accounts"][targetAccountID]["email"]

    altText = f"""
    Dear {username},
    This is a test email to ensure that the email system is working correctly.
    If you are reading this, then the email system is working correctly.

    Kindly regards, The Verdex Team
    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY VERDEX. DO NOT REPLY TO THIS EMAIL.
    {Universal.copyright}
    """
    html = render_template('emails/testEmail.html', username=username, copyright = Universal.copyright)

    email_sent = Emailer.sendEmail(email, "Test Email", altText, html)
    if email_sent:
        Logger.log("ADMIN SEND_TEST_EMAIL: Test email sent to {}.".format(email))
        return "SUCCESS: Test email sent to {}.".format(email)
    else:
        return "ERROR: Test email failed to send to {}.".format(email)
    
@apiBP.route('/api/toggleEmailer', methods=['POST'])
def toggle_emailer():
    authCheck = manageIDToken(checkIfAdmin=True)
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    emailer_current = AddonsManager.readConfigKey("EmailingServicesEnabled")
    
    if "EmailingServicesEnabled" in os.environ and os.environ["EmailingServicesEnabled"] == "True":
        if emailer_current == "Key Not Found":
            AddonsManager.setConfigKey("EmailingServicesEnabled", Emailer.servicesEnabled)
            Logger.log("ADMIN TOGGLE_EMAILER: Emailing services enabled by admin '{}'.".format(targetAccountID))
        else:
            Emailer.servicesEnabled = not emailer_current
            AddonsManager.setConfigKey("EmailingServicesEnabled", Emailer.servicesEnabled)
            Logger.log("ADMIN TOGGLE_EMAILER: Emailing services toggled to {} by admin '{}'.".format("True" if Emailer.servicesEnabled else "False", targetAccountID))
        return 'SUCCESS: Emailing services toggled.'
    else:
        return "ERROR: Emailing services are internally disabled and cannot be changed."
    
@apiBP.route('/api/toggleAnalytics', methods=['POST'])
def toggle_analytics():
    authCheck = manageIDToken(checkIfAdmin=True)
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    analyticsInternalStatus = os.environ.get("AnalyticsEnabled") == "True"

    analyticsAdminStatus = AddonsManager.readConfigKey("AnalyticsEnabled")
    if analyticsAdminStatus == "Key Not Found":
        AddonsManager.setConfigKey("AnalyticsEnabled", analyticsInternalStatus)

    if not analyticsInternalStatus:
        return "ERROR: Analytics is internally disabled. You cannot toggle it."
    
    analyticsAdminStatus = not analyticsAdminStatus
    AddonsManager.setConfigKey("AnalyticsEnabled", analyticsAdminStatus)
    Analytics.adminEnabled = analyticsAdminStatus

    if Analytics.checkPermissions():
        response = Analytics.load_metrics()
        if not response:
            Logger.log("API TOGGLE_ANALYTICS: Failed to auto-load Analytics upon admin enable.")

    Logger.log("API TOGGLE_ANALYTICS: Analytics toggled to {} by admin '{}'.".format("True" if analyticsAdminStatus else "False", targetAccountID))

    return "SUCCESS: Analytics toggled successfully."
    
@apiBP.route('/api/reload_database', methods=['POST'])
def reload_database():
    authCheck = manageIDToken(checkIfAdmin=True)
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    DI.load()
    Logger.log("ADMIN RELOAD_DATABASE: Database reloaded by admin {}.". format(targetAccountID))
    return 'SUCCESS: Database reloaded.'

@apiBP.route('/api/reload_fireauth', methods=['POST'])
def reload_fireauth():
    authCheck = manageIDToken(checkIfAdmin=True)
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if FireConn.checkPermissions():
        previousCopy = copy.deepcopy(DI.data["accounts"])
        DI.data["accounts"] = FireAuth.generateAccountsObject(fireAuthUsers=FireAuth.listUsers(), existingAccounts=DI.data["accounts"], strategy="overwrite")
        DI.save()

        if previousCopy != DI.data["accounts"]:
            print("ADMIN: Necessary database synchronisation with Firebase Authentication complete.")

    Logger.log("ADMIN RELOAD_FIREAUTH: FireAuth reloaded.")
    return 'SUCCESS: FireAuth reloaded.'

@apiBP.route('/api/reply', methods=['POST'])
def reply():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    authCheck = manageIDToken(checkIfAdmin=True)
    if not authCheck.startswith("SUCCESS"):
        return authCheck
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if "email_title" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "email_body" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "questionID" not in request.json:
        return "ERROR: One or more payload parameters are missing."
    if "supportQueries" in DI.data["admin"] and request.json["questionID"] not in DI.data["admin"]["supportQueries"]:
        return "ERROR: No such question exists."
    
    question_id = request.json['questionID']
    email_title = request.json['email_title']
    email_body = request.json['email_body']
    email_target = DI.data['admin']['supportQueries'][question_id]['email']
    email_name = DI.data['admin']['supportQueries'][question_id]['name']
    question_message = DI.data['admin']['supportQueries'][question_id]['message']
    question_timestamp = DI.data['admin']['supportQueries'][question_id]['timestamp']
    readableQuestionTimestamp = datetime.datetime.strptime(question_timestamp, Universal.systemWideStringDatetimeFormat).strftime("%d %b %Y %I:%M %p")
    
    adminName, adminPosition = getNameAndPosition(DI.data["accounts"], targetAccountID)
    altText = f"""
    ----------
    In response to this customer support message you sent on {readableQuestionTimestamp}:

    {question_message}
    ----------

    Dear {email_name},
    
    {email_body}

    Yours sincerely,
    {adminName}
    {adminPosition}
    The Verdex Team
    
    {Universal.copyright}
    """

    html = render_template('emails/adminReplyTemplate.html', 
        email_name=email_name, 
        email_body=email_body,
        email_title=email_title,
        question_message=question_message,
        adminName = adminName,
        adminPosition = adminPosition,
        question_timestamp = readableQuestionTimestamp,
        copyright = Universal.copyright
    )

    Emailer.sendEmail(email_target, email_title, altText, html)

    Analytics.add_metrics(Analytics.EventTypes.question_answered)
    
    del DI.data['admin']['supportQueries'][question_id]
    DI.save()
    return "SUCCESS: Email sent."

@apiBP.route('/api/addDay', methods=['POST'])
def addDay():
    check = checkHeaders(request.headers)
    if check != True:
        return check

    if "itineraryID" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if "dayNo" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    
    itineraryID = request.json['itineraryID']
    dayNo = str(request.json['dayNo'])

    latestDate = max((day["date"] for day in DI.data["itineraries"][itineraryID]["days"].values()), default=None) if itineraryID in DI.data["itineraries"] else None
    if latestDate == None:
        return "ERROR: Latest date is not found."

    newDate = (datetime.datetime.strptime(latestDate, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    if itineraryID in DI.data["itineraries"]:
        if "days" in DI.data["itineraries"][itineraryID]:
            if dayNo not in DI.data["itineraries"][itineraryID]["days"]:
                DI.data["itineraries"][itineraryID]["days"][dayNo] = {"date" : newDate, "activities" : {}}
                DI.save()
                return "SUCCESS: Day is added successfully."
            else:
                return "UERROR: Day already exists, can't duplicate day."
        else:
            DI.data["itineraries"][itineraryID]["days"] = {dayNo : {"date" : newDate, "activities" : {}}}
            DI.save()
            return "SUCCESS: Day is added successfully."
    else:
        return "ERROR: Itinerary ID not found in system."
            
@apiBP.route('/api/deleteDay', methods=['POST'])
def deleteDay():
    check = checkHeaders(request.headers)
    if check != True:
        return check

    if "itineraryID" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if "dayNo" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    
    itineraryID = request.json['itineraryID']
    dayNo = str(request.json['dayNo'])

    if itineraryID not in DI.data["itineraries"]:
        return "ERROR: Itinerary not found."
    
    if dayNo not in DI.data["itineraries"][itineraryID]["days"]:
        return "ERROR: Day not found, can't delete day."
    if len(DI.data["itineraries"][itineraryID]["days"]) == 1:
        return "UERROR: Can't delete the only day in the itinerary. Please delete the itinerary itself."
    
    del DI.data["itineraries"][itineraryID]["days"][dayNo]
    
    daysData = [DI.data["itineraries"][itineraryID]["days"][x] for x in DI.data["itineraries"][itineraryID]["days"]]
    newDaysObject = {}
    for i in range(len(daysData)):
        newDaysObject[str(i+1)] = daysData[i]
    
    DI.data["itineraries"][itineraryID]["days"] = newDaysObject
    DI.save()

    dayToRedirectTo = 1
    if dayNo != "1":
        dayToRedirectTo = int(dayNo) - 1

    return "SUCCESS: Day is deleted successfully. Redirect to day {}".format(dayToRedirectTo)

@apiBP.route('/api/editDate', methods=['POST'])
def editdate():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    if "itineraryID" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if "day" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if "editedDate" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    
    itineraryID = request.json['itineraryID']
    day = request.json['day']
    editedDate = request.json['editedDate']

    if itineraryID in DI.data["itineraries"]:
        for loopedDay in DI.data["itineraries"][itineraryID]["days"]:
            if DI.data["itineraries"][itineraryID]["days"][loopedDay]["date"] == editedDate:
                return "UERROR: Date already exists in the itinerary, can't duplicate date."
        if day in DI.data["itineraries"][itineraryID]["days"]:
            if DI.data["itineraries"][itineraryID]["days"][day]["date"] != editedDate:
                DI.data["itineraries"][itineraryID]["days"][day]["date"] = editedDate
                DI.save()
                return "SUCCESS: Date is edited successfully."
            else:
                return "UERROR: There were no changes to the date!"
        else:
            return "ERROR: Day not found in system."
    else:
        return "ERROR: Itinerary ID not found in system."
    
@apiBP.route('/api/verdexgpt', methods=['POST'])
def verdexgpt():
    check = checkHeaders(request.headers)
    if check != True:
        return check
    
    if "prompt" not in request.json:
        return "ERROR: One or more required payload parameters not provided."
    if not isinstance(request.json['prompt'], str):
        return "ERROR: One or more required payload parameters are incorrectly formatted."
    
    userPrompt = request.json['prompt']

    if not ("VerdexGPTEnabled" in os.environ and os.environ["VerdexGPTEnabled"] == "True"):
        return "UERROR: Verdex GPT is not available at this time. Please try again later."
    elif AddonsManager.readConfigKey("VerdexGPTEnabled") != True:
        Logger.log("API VERDEXGPT: Verdex GPT usage attempt blocked due to admin override of VerdexGPTEnabled.")
        return "UERROR: Verdex GPT is not available at this time. Please try again later."
    
    if "VerdexGPTSecretKey" not in os.environ:
        Logger.log("API VERDEXGPT: Verdex GPT usage attempt blocked due to missing VerdexGPTSecretKey.")
        return "UERROR: Verdex GPT is not available at this time. Please try again later."
    elif openAIClient == None:
        Logger.log("API VERDEXGPT: Verdex GPT usage attempt blocked due to uninitialised internal OpenAI client.")
        return "UERROR: Verdex GPT is not available at this time. Please try again later."

    try:
        response = openAIClient.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that specifically caters to topics about sustainable travel, itineraries, activities to do in Singapore and what to post on our forum, VerdexTalks. Anything unrelated to sustainable travel, food, hiking, travelling, nature, scenery, exploration, sightseeing, itineraries, activities to do in Singapore or what to post on our forum, VerdexTalks, will be answered extremely briefly and you'll ask if the user has any other questions related to sustainable travel and itineraries, or activities to do in Singapore"},
                {"role": "system", "content": "Ask the user if they have any other questions related to sustainable travel and itineraries, or activities to do in Singapore at the end of your response."},
                {"role": "system", "content": "Respond on a new line after every sentence."},
                {"role": "system", "content": "Your name is VerdexGPT."},
                {"role": "user", "content": userPrompt}
            ],
            max_tokens=450
        )

        response
        generated_text = response.choices[0].message.content
        
        Logger.log("API VERDEXGPT: Verdex GPT generated a response for prompt '{}'.".format(userPrompt))
    except Exception as e:
        Logger.log("API VERDEXGPT: Verdex GPT failed to generate a response for prompt '{}'. Error: {}".format(userPrompt, e))
        return "UERROR: Verdex GPT failed to generate a response. Please try again later."
    
    return jsonify({'generated_text': generated_text})
