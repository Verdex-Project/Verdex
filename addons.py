import os, sys, json, datetime, copy, pyrebase, uuid, googlemaps
from firebase_admin import db, storage, credentials, initialize_app
from firebase_admin import auth as adminAuth
from dotenv import load_dotenv
load_dotenv()

class AddonsManager:
    '''A key-value persistence manager for addons services.
    
    Usage:
    ```
    AddonsManager.setup()
    AddonsManager.setConfigKey("username", "johnAppleseed")
    print(AddonsManager.readConfigKey("username")) # johnAppleseed
    AddonsManager.deleteConfigKey("username")
    print(AddonsManager.readConfigKey("username")) # Key Not Found
    ```

    NOTE: This class is not meant to be instantiated. The `setup` method must be executed before executing any other methods.
    '''

    config = None

    @staticmethod
    def setup():
        try:
            if not os.path.isfile(os.path.join(os.getcwd(), 'config.txt')):
                with open('config.txt', 'w') as f:
                    f.write("{}")
            
            AddonsManager.config = json.load(open('config.txt', 'r'))
            return "Success"
        except Exception as e:
            return "ERROR: Failed to check for config file and create a new one if there isn't one; error: {}".format(e)

    @staticmethod
    def setConfigKey(keyName, value):
        '''Returns "Success" upon successful execution. Requries `setup` method to be executed first.'''
        try:
            AddonsManager.config[keyName] = value
            json.dump(AddonsManager.config, open('config.txt', 'w'))
            return "Success"
        except Exception as e:
            return "ERROR: Failed to set config key; error: {}".format(e)

    @staticmethod
    def readConfigKey(keyName):
        '''Returns the value of the key if it exists, otherwise returns "Key Not Found". Requries `setup` method to be executed first.'''
        try:
            if keyName not in AddonsManager.config:
                return "Key Not Found"
            return AddonsManager.config[keyName]
        except Exception as e:
            return "ERROR: Failed to read config key; error: {}".format(e)
    
    @staticmethod
    def deleteConfigKey(keyName):
        '''Returns "Success" upon successful execution. Requries `setup` method to be executed first.'''
        try:
            if keyName not in AddonsManager.config:
                return "Key Not Found"
            del AddonsManager.config[keyName]
            json.dump(AddonsManager.config, open('config.txt', 'w'))
        except Exception as e:
            return "ERROR: Failed to delete config key; error: {}".format(e)
        
class FireConn:
    '''A class that manages the admin connection to Firebase via the firebase_admin module.
    
    Explicit permission has to be granted by setting `FireConnEnabled` to `True` in the .env file. `serviceAccountKey.json` file must be in working directory to provide credentials for the connection. Obtain one on the Firebase Console (under Service Accounts > Firebase Admin SDK > Generate new private key).

    Usage:

    ```
    response = FireConn.connect()
    if response != True:
        print("Error in setting up FireConn; error: " + response)
        sys.exit(1)
    ```

    NOTE: This class is not meant to be instantiated. Other services relying on connection via firebase_admin module need to run the `connect` method in this class first. If permission is not granted, dependant services may not be able to operate.
    '''
    connected = False

    @staticmethod
    def checkPermissions():
        return ("FireConnEnabled" in os.environ and os.environ["FireConnEnabled"] == "True")

    @staticmethod
    def connect():
        '''Returns True upon successful connection.'''
        if not FireConn.checkPermissions():
            return "ERROR: Firebase connection permissions are not granted."
        if not os.path.exists("serviceAccountKey.json"):
            return "ERROR: Failed to connect to Firebase. The file serviceAccountKey.json was not found. Please re-read instructions for the Firebase addon."
        else:
            if 'RTDB_URL' not in os.environ:
                return "ERROR: Failed to connect to Firebase. RTDB_URL environment variable not set in .env file. Please re-read instructions for the Firebase addon."
            try:
                ## Firebase
                cred_obj = credentials.Certificate(os.path.join(os.getcwd(), "serviceAccountKey.json"))
                default_app = initialize_app(cred_obj, {
                    'databaseURL': os.environ["RTDB_URL"],
                    "storageBucket": os.environ["STORAGE_URL"]
                })
                FireConn.connected = True
            except Exception as e:
                return "ERROR: Error occurred in connecting to RTDB; error: {}".format(e)
            return True

class FireRTDB:
    '''A class to update Firebase Realtime Database (RTDB) references with data.

    Explicit permission has to be granted by setting `FireRTDBEnabled` to `True` in the .env file.

    Usage:
    ```
    if FireRTDB.checkPermissions():
        data = {"name": "John Appleseed"}
        FireRTDB.setRef(data, refPath="/")
        fetchedData = FireRTDB.getRef(refPath="/")
        print(fetchedData) ## same as data defined above
    ```

    Advanced Usage:
    ```
    ## DB translation
    db = {"jobs": {}}
    safeForCloudDB = FireRTDB.translateForCloud(db) ## {"jobs": 0}
    # safeForLocalDB = FireRTDB.translateForLocal(safeForCloudDB) ## {"jobs": {}}
    ```

    `FireRTDB.translateForCloud` and `FireRTDB.translateForLocal` are used to translate data structures for cloud and local storage respectively. This is because Firebase does not allow null objects to be stored in the RTDB. This method converts null objects to a value that can be stored in the RTDB. The following conversions are performed:
    - Converts `{}` to `0` and `[]` to `1` (for cloud storage)
    - Converts `0` to `{}` and `1` to `[]` (for local storage)

    NOTE: This class is not meant to be instantiated. `FireConn.connect()` method must be executed before executing any other methods in this class.
    '''

    @staticmethod
    def checkPermissions():
        '''Returns True if permission is granted, otherwise returns False.'''
        if 'FireRTDBEnabled' in os.environ and os.environ['FireRTDBEnabled'] == 'True':
            return True
        return False

    @staticmethod
    def clearRef(refPath="/"):
        '''Returns True upon successful update. Providing `refPath` is optional; will be the root reference if not provided.'''
        if not FireRTDB.checkPermissions():
            return "ERROR: FireRTDB service operation permission denied."
        try:
            ref = db.reference(refPath)
            ref.set({})
        except Exception as e:
            return "ERROR: Error occurred in clearing children at that ref; error: {}".format(e)
        return True

    @staticmethod
    def setRef(data, refPath="/"):
        '''Returns True upon successful update. Providing `refPath` is optional; will be the root reference if not provided.'''
        if not FireRTDB.checkPermissions():
            return "ERROR: FireRTDB service operation permission denied."
        try:
            ref = db.reference(refPath)
            ref.set(data)
        except Exception as e:
            return "ERROR: Error occurred in setting data at that ref; error: {}".format(e)
        return True

    @staticmethod
    def getRef(refPath="/"):
        '''Returns a dictionary of the data at the specified ref. Providing `refPath` is optional; will be the root reference if not provided.'''
        if not FireRTDB.checkPermissions():
            return "ERROR: FireRTDB service operation permission denied."
        data = None
        try:
            ref = db.reference(refPath)
            data = ref.get()
        except Exception as e:
            return "ERROR: Error occurred in getting data from that ref; error: {}".format(e)
        
        if data == None:
            return {}
        else:
            return data
        
    @staticmethod
    def recursiveReplacement(obj, purpose):
        dictValue = {} if purpose == 'cloud' else 0
        dictReplacementValue = 0 if purpose == 'cloud' else {}

        arrayValue = [] if purpose == 'cloud' else 1
        arrayReplacementValue = 1 if purpose == 'cloud' else []

        data = copy.deepcopy(obj)

        for key in data:
            if isinstance(data, list):
                # This if statement forbids the following sub-data-structure: [{}, 1, {}] (this is an example)
                continue

            if isinstance(data[key], dict):
                if data[key] == dictValue:
                    data[key] = dictReplacementValue
                else:
                    data[key] = FireRTDB.recursiveReplacement(data[key], purpose)
            elif isinstance(data[key], list):
                if data[key] == arrayValue:
                    data[key] = arrayReplacementValue
                else:
                    data[key] = FireRTDB.recursiveReplacement(data[key], purpose)
            elif isinstance(data[key], bool):
                continue
            elif isinstance(data[key], int) and purpose == 'local':
                if data[key] == 0:
                    data[key] = {}
                elif data[key] == 1:
                    data[key] = []

        return data
    
    @staticmethod
    def translateForLocal(fetchedData):
        '''Returns a translated data structure that can be stored locally.'''
        tempData = copy.deepcopy(fetchedData)

        try:
            # Null object replacement
            tempData = FireRTDB.recursiveReplacement(obj=tempData, purpose='local')

            # TODO: Perform email translation (convert commas to dots)
        except Exception as e:
            return "ERROR: Error in translating fetched RTDB data for local system use; error: {}".format(e)
        
        return tempData
    
    @staticmethod
    def translateForCloud(loadedData):
        '''Returns a translated data structure that can be stored in the cloud.'''
        tempData = copy.deepcopy(loadedData)

        # TODO: Perform email translation (convert dots to commas)

        # Null object replacement
        tempData = FireRTDB.recursiveReplacement(obj=tempData, purpose='cloud')

        return tempData
    
class FireStorage:
    '''A class to upload and download files to and from Firebase Storage.
    
    Explicit permission has to be granted by setting `FireStorageEnabled` to `True` in the .env file. `STORAGE_URL` variable must be set in .env file. Obtain one by copying the bucket URL in Storage on the Firebase Console.

    Usage:
    ```
    response = FireStorage.uploadFile(localFilePath="test.txt", filename="test.txt")
    if response != True:
        print("Error in uploading file; error: " + response)
        sys.exit(1)

    response = FireStorage.downloadFile(localFilePath="downloadedTest.txt", filename="test.txt")
    if response != True:
        print("Error in downloading file; error: " + response)
        sys.exit(1)
    ```

    NOTE: This class is not meant to be instantiated. `FireConn.connect()` method must be executed before executing any other methods in this class.
    '''

    @staticmethod
    def checkPermissions():
        '''Returns True if permission is granted, otherwise returns False.'''
        return ('FireStorageEnabled' in os.environ and os.environ['FireStorageEnabled'] == 'True')

    @staticmethod
    def uploadFile(localFilePath, filename=None):
        '''Returns True upon successful upload.'''
        if not FireStorage.checkPermissions():
            return "ERROR: FireStorage service operation permission denied."
        if filename == None:
            filename = os.path.basename(localFilePath)
        try:
            bucket = storage.bucket()
            blob = bucket.blob(filename)
            blob.upload_from_filename(localFilePath)
        except Exception as e:
            return "ERROR: Error occurred in uploading file to cloud storage; error: {}".format(e)
        return True

    @staticmethod
    def downloadFile(localFilePath, filename=None):
        '''Returns True upon successful download.'''
        if not FireStorage.checkPermissions():
            return "ERROR: FireStorage service operation permission denied."
        if filename == None:
            filename = os.path.basename(localFilePath)
        try:
            bucket = storage.bucket()
            blob = bucket.blob(filename)
            blob.download_to_filename(localFilePath)
        except Exception as e:
            return "ERROR: Error occurred in downloading file from cloud storage; error: {}".format(e)
        return True
    
class FireAuth:
    '''A class to manage authentication via Firebase Authentication.

    Relies on `pyrebase` module (`pip install pyrebase4`) that establishes a client connection to Firebase Authentication. 
    Explicit permission has to be granted by setting `FireAuthEnabled` to `True` in the .env file. 
    `FireAPIKey`, `FireAuthDomain`, `RTDB_URL`, and `STORAGE_URL` variables must be set in .env file. Obtain them on the Firebase Console.

    Some methods in this class require an admin connection via `firebase_admin` and thus require `FireConn.connect()` to be executed first.

    NOTE: This class is not meant to be instantiated. The `FireAuth.connect()` method must be executed before executing any other methods.
    '''

    auth = None

    try:
        config = {
            "apiKey": os.environ["FireAPIKey"],
            "authDomain": os.environ["FireAuthDomain"],
            "databaseURL": os.environ["RTDB_URL"],
            "storageBucket": os.environ["STORAGE_URL"]
        }
    except Exception as e:
        print("FIREAUTH INITIALISATION ERROR: Failed to set up config; error: {}".format(e))
        sys.exit(1)

    @staticmethod
    def connect():
        try:
            FireAuth.auth = pyrebase.initialize_app(FireAuth.config).auth()
            return True
        except Exception as e:
            print(f"FIREAUTH ERROR: Failed to connect to Firebase; error: {e}")
            return False
    
    @staticmethod
    def createUser(email, password):
        '''Usage:

        ```
        if FireAuth.checkPermissions() and FireAuth.connect():
            ## Create user (password must be minimum six characters
            responseObject = FireAuth.createUser(email="test@example.com", password="123456")
            if "ERROR" in responseObject:
                print(responseObject)
                exit()
            ### Parameters in responseObject (of type `dict` in success case): idToken, refreshToken, expiresIn (1 hour from login)
        ```
        '''

        try:
            signedInUser = FireAuth.auth.create_user_with_email_and_password(email, password)

            responseObject = {}
            responseObject["idToken"] = signedInUser["idToken"]
            responseObject["refreshToken"] = signedInUser["refreshToken"]
            responseObject["expiresIn"] = signedInUser["expiresIn"]
            responseObject["uid"] = signedInUser["localId"]

            return responseObject
        except Exception as e:
            return "ERROR: Failed to create user; error response: {}".format(e)
    
    @staticmethod
    def login(email, password):
        '''Usage:
        
        ```
        if FireAuth.checkPermissions() and FireAuth.connect():
            ## Login (FYI, create user already logs in the user)
            responseObject = FireAuth.login(email="test@example.com", password="123456")
            if "ERROR" in responseObject:
                print(responseObject)
                exit()
            ### Parameters in responseObject (of type `dict` in success case): idToken, refreshToken, expiresIn (1 hour from login)
        ```
        '''

        try:
            signedInUser = FireAuth.auth.sign_in_with_email_and_password(email, password)

            responseObject = {}
            responseObject["idToken"] = signedInUser["idToken"]
            responseObject["refreshToken"] = signedInUser["refreshToken"]
            responseObject["expiresIn"] = signedInUser["expiresIn"]

            return responseObject
        except Exception as e:
            return "ERROR: Invalid credentials; error response: {}".format(e)
    
    @staticmethod
    def accountInfo(idToken, includePassHash=False):
        '''Usage:

        ```
        if FireAuth.checkPermissions() and FireAuth.connect():
            ## Get account info
            responseObject = FireAuth.accountInfo(idToken=responseObject["idToken"])
            if "ERROR" in responseObject:
                print(responseObject)
                exit()
            ### Parameters in responseObject (of type `dict` in success case): localId, email, emailVerified, displayName, photoUrl, passwordHash, passwordUpdatedAt, validSince, disabled, lastLoginAt, createdAt, customAuth, providerUserInfo, lastRefreshAt
        ```
        '''

        try:
            info = FireAuth.auth.get_account_info(idToken)

            responseObject = {}

            ## Extract account data
            for parameter in info["users"][0]:
                if includePassHash and parameter == "passwordHash":
                    responseObject[parameter] = info["users"][0][parameter]
                elif parameter == "providerUserInfo":
                    for userInfoParam in info["users"][0][parameter][0]:
                        if userInfoParam != "email":
                            responseObject[userInfoParam] = info["users"][0][parameter][0][userInfoParam]
                elif parameter == "localId":
                    responseObject["uid"] = info["users"][0][parameter]
                elif parameter != "passwordHash":
                    responseObject[parameter] = info["users"][0][parameter]

            return responseObject
        except Exception as e:
            return "ERROR: Invalid ID token; error response: {}".format(e)

    @staticmethod
    def refreshToken(refreshToken):
        '''Usage:

        ```
        if FireAuth.checkPermissions() and FireAuth.connect():
            ## Refresh token
            responseObject = FireAuth.refreshToken(refreshToken=responseObject["refreshToken"])
            if "ERROR" in responseObject:
                print(responseObject)
                exit()
            ### Parameters in responseObject (of type `dict` in success case): userId, idToken, refreshToken
        ```
        '''

        try:
            responseObject = FireAuth.auth.refresh(refreshToken)
            return responseObject
        except Exception as e:
            return "ERROR: Invalid refresh token; error response: {}".format(e)
        
    @staticmethod
    def deleteAccount(idToken):
        '''Returns True upon successful account deletion.

        Usage:

        ```
        FireAuth.connect()
        FireConn.connect()
        loginResponse = FireAuth.login(email="test@example.com", password="123456")
        if "ERROR" in loginResponse:
            print(loginResponse)
            exit()

        response = FireAuth.deleteAccount(loginResponse["idToken"])
        if isinstance(response, str):
            print(response)
            exit()
        ```
        
        NOTE: This method uses firebase_admin rather than pyrebase unlike the other methods in this class. `FireConn.connect()` needs to be executed successfully prior to execution of this method.
        '''

        if ((not FireConn.checkPermissions()) or (not FireConn.connected)):
            return "ERROR: Delete account requires a Firebase connection granted by explicit permission."
        
        try:
            fireAuthUserID = FireAuth.accountInfo(idToken)["uid"]
            adminAuth.delete_user(fireAuthUserID)
            return True
        except Exception as e:
            return "ERROR: Failed to delete account; error response: {}".format(e)
        
    @staticmethod
    def listUsers():
        '''Returns a list of all users in Firebase Authentication.

        Returns a `FirebaseAdmin.Auth.ExportedUserRecord` object for each user.

        Usage:
        ```
        FireAuth.connect()
        FireConn.connect()
        users = FireAuth.listUsers()
        if isinstance(users, str):
            print(users)
            exit()
        for user in users:
            print(user.uid)
            print(user.email)
        ```

        NOTE: This method uses firebase_admin rather than pyrebase unlike some other methods in this class. `FireConn.connect()` needs to be executed successfully prior to execution of this method.
        '''

        if ((not FireConn.checkPermissions()) or (not FireConn.connected)):
            return "ERROR: List users requires a Firebase connection granted by explicit permission."
        
        users = []
        try:
            for user in adminAuth.list_users().iterate_all():
                users.append(user)
            return users
        except Exception as e:
            return "ERROR: Failed to list users; error response: {}".format(e)
        
    @staticmethod
    def generateAccountsObject(fireAuthUsers, existingAccounts, strategy="add-only"):
        '''## Intro
        Returns an accounts object that can be used to update the accounts object in DI.

        This method could be used for synchronisation purposes of the database with the account records on Firebase Authentication.
        There are three strategies that can be used:
        - `overwrite`: Overwrites the accounts object with the accounts data fetched from Firebase Authentication. Removes users not on Firebase and adds users on Firebase that are not in the accounts object.
        - `add-only`: Adds users from Firebase Authentication that are not in the accounts object. This is the DEFAULT strategy and probably the safest one. However, always sticking to add-only will result in the accounts object being bloated with users that are not on Firebase Authentication.
        - `remove-only`: Removes users from the accounts object that are not on Firebase Authentication.

        ## SAMPLE Usage:
        ```
        FireAuth.connect()
        FireConn.connect()
        DI.data["accounts"] = FireAuth.generateAccountsObject(fireAuthUsers=FireAuth.listUsers(), existingAccounts=DI.data["accounts"], strategy="overwrite")
        DI.save()
        ```

        NOTE: This method does not directly use any Firebase connection. But, you may need to use the `FireAuth.listUsers()` method which requires that `FireConn.connect()` is executed successfully prior.
        '''

        if strategy not in ['overwrite', 'add-only', 'remove-only']:
            return "ERROR: Invalid strategy."
        
        accounts = copy.deepcopy(existingAccounts)

        existingAccountIDs = [accounts[localID]["fireAuthID"] for localID in accounts]
        if strategy == 'overwrite' or strategy == 'add-only':
            ## Add users on Firebase that are not in the accounts object
            for fireUser in fireAuthUsers:
                if fireUser.uid not in existingAccountIDs:
                    newLocalID = uuid.uuid4().hex
                    accounts[newLocalID] = {
                        "id": newLocalID,
                        "fireAuthID": fireUser.uid,
                        "username": "Not Set",
                        "email": fireUser.email,
                        "password": "Not Set",
                    }
        
        if strategy == 'overwrite' or strategy == 'remove-only':
            ## Remove users from accounts object that are not on Firebase
            for fireAuthID in existingAccountIDs:
                if fireAuthID not in [fireUser.uid for fireUser in fireAuthUsers]:
                    for localID in accounts:
                        if accounts[localID]["fireAuthID"] == fireAuthID:
                            del accounts[localID]
                            break

        return accounts
    
class GoogleMapsService:
    servicesEnabled = False
    contextChecked = False
    gmapsAPIKey = None
    gmapsClient = None

    @staticmethod
    def checkContext():
        if "GoogleMapsEnabled" in os.environ and os.environ["GoogleMapsEnabled"] == "True":
            GoogleMapsService.gmapsClient = googlemaps.Client(key=os.environ["GoogleMapsAPIKey"])
            GoogleMapsService.gmapsAPIKey = os.environ["GoogleMapsAPIKey"]
            GoogleMapsService.servicesEnabled = True
            GoogleMapsService.contextChecked = True
        
    @staticmethod
    def generateMapEmbedHTML(mapMode, mapType, zoom="default", classlist="", id="", width="600", height="450", placeQuery=None, directionsOrigin=None, directionsDestination=None, directionsMode=None, viewCenterCoordinates=None):
        # Check permission        
        if not GoogleMapsService.servicesEnabled:
            return "ERROR: Google Maps services are not enabled."
        
        # Validate inputs
        if mapMode not in ["place", "directions", "view"]:
            return "ERROR: Invalid map mode."
        if mapType not in ["roadmap", "satellite"]:
            return "ERROR: Invalid map type."
        
        ## Mode-based data validation
        if mapMode == "place" and placeQuery == None:
            return "ERROR: Place query not provided for place map mode."
        if mapMode == "directions":
            if directionsOrigin == None or directionsDestination == None or directionsMode == None:
                return "ERROR: Directions origin, destination and commute mode not provided for directions map mode."
            elif directionsMode not in ["driving", "walking", "bicycling", "transit", "flying"]:
                return "ERROR: Invalid directions mode."
        if mapMode == "view" and viewCenterCoordinates == None:
            return "ERROR: View center coordinates not provided for view map mode."
        
        # Formulate request parameters
        parameters = ["key={}".format(GoogleMapsService.gmapsAPIKey)]
        if mapMode == "place":
            parameters += [
                "q={}".format(placeQuery),
                "maptype={}".format(mapType)
            ]
        elif mapMode == "directions":
            parameters += [
                "origin={}".format(directionsOrigin),
                "destination={}".format(directionsDestination),
                "mode={}".format(directionsMode),
                "units=metric",
                "maptype={}".format(mapType)
            ]
        elif mapMode == "view":
            parameters += [
                "center={}".format(viewCenterCoordinates),
                "maptype={}".format(mapType)
            ]

        if zoom != "default":
            parameters.append("zoom={}".format(zoom))
        if mapMode != "view" and viewCenterCoordinates != None:
            parameters.append("center={}".format(viewCenterCoordinates))

        # Formulate HTML
        embedHTML = "<iframe class='{}' id='{}' width='{}' height='{}' frameborder='0' style='border:0' src='https://www.google.com/maps/embed/v1/{}?{}' allowfullscreen></iframe>".format(classlist, id, width, height, mapMode, "&".join(parameters))
        return embedHTML
    
    @staticmethod
    def generateRoute(startLocation: str, endLocation: str, mode: str, departureTime):
        # Check permission        
        if not GoogleMapsService.servicesEnabled:
            return "ERROR: Google Maps services are not enabled."
        
        if (not isinstance(startLocation, str)) or (not isinstance(endLocation, str)) or (not isinstance(mode, str)) or (not isinstance(departureTime, datetime.datetime)):
            return "ERROR: Invalid start or end location. Both must be a string."
        elif mode not in ["driving", "walking", "bicycling", "transit", "flying"]:
            return "ERROR: Invalid directions mode."
        
        # Obtain directions data from Google Maps
        try:
            directionsData = GoogleMapsService.gmapsClient.directions(startLocation, endLocation, mode=mode, departure_time=departureTime)
        except Exception as e:
            return "ERROR: Failed to obtain directions data from Google Maps; error: {}".format(e)
        
        # Extract and process relevant data
        directionsData = directionsData[0]
        response = {}
        response["copyright"] = directionsData["copyrights"]
        response["warnings"] = directionsData["warnings"]
        response["steps"] = []

        leg = directionsData["legs"][0]
        ## Process legs
        for step in leg["steps"]:
            travelMode = step["travel_mode"]
            if travelMode == "TRANSIT":
                # response["steps"][directionsData["steps"].index(step)]["transit_details"] = step["transit_details"]
                response["steps"][directionsData["steps"].index(step)] = {
                    "": ""
                }