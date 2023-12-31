import os, json, sys, random, datetime, copy, base64
from passlib.hash import sha256_crypt as sha
from addons import *

def fileContent(filePath, passAPIKey=False):
    with open(filePath, 'r') as f:
        f_content = f.read()
        if passAPIKey:
            f_content = f_content.replace("\{{ API_KEY }}", os.getenv("API_KEY"))
        return f_content

# DatabaseInterface class
class DI:
    data = []

    sampleData = {
        "accounts": {},
        "itineraries": {},
        "forum": {}
    }

    @staticmethod
    def setup():
        if not os.path.exists(os.path.join(os.getcwd(), "database.txt")):
            with open("database.txt", "w") as f:
                json.dump(DI.sampleData, f)
        
        if FireRTDB.checkPermissions():
            print("DI: Firebase RTDB is enabled. Connecting to Firebase...")
            try:
                response = FireConn.connect()
                if response != True:
                    print("DI FIRECONN ERROR: " + response)
                    return "Error"
                
                print("DI: Connected to Firebase!")
            except Exception as e:
                print("DI FIRECONN ERROR: " + str(e))
                return "Error"
            
        return DI.load()
    
    @staticmethod
    def load():
        try:
            if not os.path.exists(os.path.join(os.getcwd(), "database.txt")):
                with open("database.txt", "w") as f:
                    json.dump(DI.sampleData, f)
            
            if FireRTDB.checkPermissions():
                # Fetch data from RTDB
                fetchedData = FireRTDB.getRef()
                if isinstance(fetchedData, str) and fetchedData.startswith("ERROR"):
                    # Trigger last resort of local database (Auto-repair)
                    print("DI-FIRERTDB GETREF ERROR: " + fetchedData)
                    print("DI: System will try to resort to local database to load data to prevent a crash. Attempts to sync with RTDB will continue.")

                    # Read data from local database file
                    with open("database.txt", "r") as f:
                        DI.data = json.load(f)
                    return "Success"
                
                # Translate data for local use
                fetchedData = FireRTDB.translateForLocal(fetchedData)
                if isinstance(fetchedData, str) and fetchedData.startswith("ERROR"):
                    # Trigger last resort of local database (Auto-repair)
                    print("DI-FIRERTDB TRANSLATELOCAL ERROR: " + fetchedData)
                    print("DI: System will try to resort to local database to load data to prevent a crash. Attempts to sync with RTDB will continue.")

                    # Read data from local database file
                    with open("database.txt", "r") as f:
                        DI.data = json.load(f)
                    return "Success"
                
                # Write data to local db file
                if fetchedData != None and fetchedData != {}:
                    with open("database.txt", "w") as f:
                        json.dump(fetchedData, f)
                    
                    # Load data into DI
                    DI.data = fetchedData
                else:
                    # RTDB is empty and sample structure needs to be written
                    response = FireRTDB.setRef(FireRTDB.translateForCloud(DI.sampleData))
                    if response != True:
                        print("DI-FIRERTDB SETREF ERROR: " + response)
                        print("DI: Failed to set sample structure in RTDB. System will resort to local database but attempts to sync will continue.")
                        with open("database.txt", "r") as f:
                            DI.data = json.load(f)
                        return "Success"
            else:
                # Read data from local database file
                with open("database.txt", "r") as f:
                    DI.data = json.load(f)
                return "Success"
        except Exception as e:
            print("DI ERROR: Failed to load data from database; error: {}".format(e))
            return "Error"
        return "Success"
    
    @staticmethod
    def save():
        try:
            with open("database.txt", "w") as f:
                json.dump(DI.data, f)

            # Update RTDB
            if FireRTDB.checkPermissions():
                response = FireRTDB.setRef(FireRTDB.translateForCloud(DI.data))
                if response != True:
                    print("DI FIRERTDB SETREF ERROR: " + response)
                    print("DI: System will resort to local database to prevent a crash. Attempts to sync with RTDB will continue.")
                    # Continue runtime as system can function without cloud database
        except Exception as e:
            print("DI ERROR: Failed to save data to database; error: {}".format(e))
            return "Error"
        return "Success"

class Encryption:
    @staticmethod
    def encodeToB64(inputString):
        hash_bytes = inputString.encode("ascii")
        b64_bytes = base64.b64encode(hash_bytes)
        b64_string = b64_bytes.decode("ascii")
        return b64_string
    
    @staticmethod
    def decodeFromB64(encodedHash):
        b64_bytes = encodedHash.encode("ascii")
        hash_bytes = base64.b64decode(b64_bytes)
        hash_string = hash_bytes.decode("ascii")
        return hash_string
  
    @staticmethod
    def isBase64(encodedHash):
        try:
            hashBytes = encodedHash.encode("ascii")
            return base64.b64encode(base64.b64decode(hashBytes)) == hashBytes
        except Exception:
            return False

    @staticmethod
    def encodeToSHA256(string):
        return sha.hash(string)
  
    @staticmethod
    def verifySHA256(inputString, hash):
        return sha.verify(inputString, hash)
  
    @staticmethod
    def convertBase64ToSHA(base64Hash):
        return Encryption.encodeToSHA256(Encryption.decodeFromB64(base64Hash))
    
class Universal:
    systemWideStringDatetimeFormat = "%Y-%m-%d %H:%M:%S"