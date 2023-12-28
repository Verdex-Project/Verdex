import os, sys, json, datetime, copy
import firebase_admin
from firebase_admin import db
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
        if 'FireRTDBEnabled' in os.environ and os.environ['FireRTDBEnabled'] == 'True':
            return True
        else:
            return False

    @staticmethod
    def connect():
        if not os.path.exists("serviceAccountKey.json"):
            return "ERROR: Failed to connect to Firebase. The file serviceAccountKey.json was not found. Please re-read instructions for the Firebase addon."
        else:
            if 'RTDB_URL' not in os.environ:
                return "ERROR: Failed to connect to Firebase. RTDB_URL environment variable not set in .env file. Please re-read instructions for the Firebase addon."
            try:
                ## Firebase
                cred_obj = firebase_admin.credentials.Certificate(os.path.join(os.getcwd(), "serviceAccountKey.json"))
                default_app = firebase_admin.initialize_app(cred_obj, { 'databaseURL': os.environ["RTDB_URL"] })
            except Exception as e:
                return "ERROR: Error occurred in connecting to RTDB; error: {}".format(e)
            return True

class FireRTDB:
    @staticmethod
    def clearRef(refPath="/"):
        try:
            ref = db.reference(refPath)
            ref.set({})
        except Exception as e:
            return "ERROR: Error occurred in clearing children at that ref; error: {}".format(e)
        return True

    @staticmethod
    def setRef(data, refPath="/"):
        try:
            ref = db.reference(refPath)
            ref.set(data)
        except Exception as e:
            return "ERROR: Error occurred in setting data at that ref; error: {}".format(e)
        return True

    @staticmethod
    def getRef(refPath="/"):
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