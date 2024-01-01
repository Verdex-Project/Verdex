import os, sys, json, datetime, copy, pyrebase
from firebase_admin import db, storage, credentials, initialize_app
from dotenv import load_dotenv
load_dotenv()

class AddonsManager:
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
        try:
            AddonsManager.config[keyName] = value
            json.dump(AddonsManager.config, open('config.txt', 'w'))
            return "Success"
        except Exception as e:
            return "ERROR: Failed to set config key; error: {}".format(e)

    @staticmethod
    def readConfigKey(keyName):
        try:
            if keyName not in AddonsManager.config:
                return "Key Not Found"
            return AddonsManager.config[keyName]
        except Exception as e:
            return "ERROR: Failed to read config key; error: {}".format(e)
    
    @staticmethod
    def deleteConfigKey(keyName):
        try:
            if keyName not in AddonsManager.config:
                return "Key Not Found"
            del AddonsManager.config[keyName]
            json.dump(AddonsManager.config, open('config.txt', 'w'))
        except Exception as e:
            return "ERROR: Failed to delete config key; error: {}".format(e)
        
class FireConn:
    @staticmethod
    def checkPermissions():
        enabledEnvVars = ["FireRTDBEnabled", "FireStorageEnabled"]
        for envVar in enabledEnvVars:
            if envVar in os.environ and os.environ[envVar] == 'True':
                return True
        return False

    @staticmethod
    def connect():
        if not FireConn.checkPermissions():
            return "ERROR: No Firebase services are enabled in the .env file to grant permission to connect to Firebase."
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
            except Exception as e:
                return "ERROR: Error occurred in connecting to RTDB; error: {}".format(e)
            return True

class FireRTDB:
    @staticmethod
    def checkPermissions():
        if 'FireRTDBEnabled' in os.environ and os.environ['FireRTDBEnabled'] == 'True':
            return True
        return False

    @staticmethod
    def clearRef(refPath="/"):
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
        tempData = copy.deepcopy(loadedData)

        # TODO: Perform email translation (convert dots to commas)

        # Null object replacement
        tempData = FireRTDB.recursiveReplacement(obj=tempData, purpose='cloud')

        return tempData
    
class FireStorage:
    @staticmethod
    def checkPermissions():
        if 'FireStorageEnabled' in os.environ and os.environ['FireStorageEnabled'] == 'True':
            return True
        return False

    @staticmethod
    def uploadFile(localFilePath, filename=None):
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
    auth = None

    config = {
        "apiKey": os.environ["FireAPIKey"],
        "authDomain": os.environ["FireAuthDomain"],
        "databaseURL": os.environ["RTDB_URL"],
        "storageBucket": os.environ["STORAGE_URL"]
    }

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
        try:
            signedInUser = FireAuth.auth.create_user_with_email_and_password(email, password)

            responseObject = {}
            responseObject["idToken"] = signedInUser["idToken"]
            responseObject["refreshToken"] = signedInUser["refreshToken"]
            responseObject["expiresIn"] = signedInUser["expiresIn"]

            return responseObject
        except Exception as e:
            return "ERROR: Failed to create user; error response: {}".format(e)
    
    @staticmethod
    def login(email, password):
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
                elif parameter != "passwordHash":
                    responseObject[parameter] = info["users"][0][parameter]

            return responseObject
        except Exception as e:
            return "ERROR: Invalid ID token; error response: {}".format(e)