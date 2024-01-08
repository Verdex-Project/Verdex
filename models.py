import os, json, sys, random, datetime, copy, base64, uuid
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
            try:
                if not FireConn.connected:
                    print("DI-FIRECONN: Firebase connection not established. Attempting to connect...")
                    response = FireConn.connect()
                    if response != True:
                        print("DI-FIRECONN: Failed to connect to Firebase. Aborting setup.")
                        return "Error"
                    else:
                        print("DI-FIRECONN: Firebase connection established. Firebase RTDB is enabled.")
                else:
                    print("DI: Firebase RTDB is enabled.")
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

    @staticmethod
    def generateUniqueID():
        return uuid.uuid4().hex

class Logger:
  @staticmethod
  def checkPermission():
      if "LoggingEnabled" in os.environ and os.environ["LoggingEnabled"] == 'True':
          return True
      else:
          return False

  @staticmethod
  def setup():
    if Logger.checkPermission():
        try:
            if not os.path.exists(os.path.join(os.getcwd(), "logs.txt")):
                with open("logs.txt", "w") as f:
                    f.write("{}UTC {}\n".format(datetime.datetime.now().utcnow().strftime(Universal.systemWideStringDatetimeFormat), "LOGGER: Logger database file setup complete."))
        except Exception as e:
            print("LOGGER SETUP ERROR: Failed to setup logs.txt database file. Setup permissions have been granted. Error: {}".format(e))

    return

  @staticmethod
  def log(message):
    if Logger.checkPermission():
        try:
            with open("logs.txt", "a") as f:
                f.write("{}UTC {}\n".format(datetime.datetime.now().utcnow().strftime(Universal.systemWideStringDatetimeFormat), message))
        except Exception as e:
            print("LOGGER LOG ERROR: Failed to log message. Error: {}".format(e))
        
    return
    
  @staticmethod
  def destroyAll():
    try:
        if os.path.exists(os.path.join(os.getcwd(), "logs.txt")):
            os.remove("logs.txt")
    except Exception as e:
        print("LOGGER DESTROYALL ERROR: Failed to destroy logs.txt database file. Error: {}".format(e))

  @staticmethod
  def readAll():
    if not Logger.checkPermission():
        return "ERROR: Logging-related services do not have permission to operate."
    try:
        if os.path.exists(os.path.join(os.getcwd(), "logs.txt")):
            with open("logs.txt", "r") as f:
                logs = f.readlines()
                for logIndex in range(len(logs)):
                    logs[logIndex] = logs[logIndex].replace("\n", "")
                return logs
        else:
            return []
    except Exception as e:
        print("LOGGER READALL ERROR: Failed to check and read logs.txt database file. Error: {}".format(e))
        return "ERROR: Failed to check and read logs.txt database file. Error: {}".format(e)
      
  @staticmethod
  def manageLogs():
    permission = Logger.checkPermission()
    if not permission:
        print("LOGGER: Logging-related services do not have permission to operate. Set LoggingEnabled to True in .env file to enable logging.")
        return
    
    print("LOGGER: Welcome to the Logging Management Console.")
    while True:
        print("""
Commands:
    read <number of lines, e.g 50 (optional)>: Reads the last <number of lines> of logs. If no number is specified, all logs will be displayed.
    destroy: Destroys all logs.
    exit: Exit the Logging Management Console.
""")
    
        userChoice = input("Enter command: ")
        userChoice = userChoice.lower()
        while not userChoice.startswith("read") and (userChoice != "destroy") and (userChoice != "exit"):
            userChoice = input("Invalid command. Enter command: ")
            userChoice = userChoice.lower()
    
        if userChoice.startswith("read"):
            allLogs = Logger.readAll()

            userChoice = userChoice.split(" ")
            logCount = 0
            if len(userChoice) != 1:
                try:
                    logCount = int(userChoice[1])
                    if logCount > len(allLogs):
                        logCount = len(allLogs)
                    elif logCount <= 0:
                        raise Exception("Invalid log count. Must be a positive integer above 0 lower than or equal to the total number of logs.")
                except Exception as e:
                    print("LOGGER: Failed to read logs. Error: {}".format(e))
                    continue
            else:
                logCount = len(allLogs)

            targetLogs = allLogs[-logCount:]
            print()
            print("Displaying {} log entries:".format(logCount))
            print()
            for log in targetLogs:
                print("\t{}".format(log))
        elif userChoice == "destroy":
            Logger.destroyAll()
            print("LOGGER: All logs destroyed.")
        elif userChoice == "exit":
            print("LOGGER: Exiting Logging Management Console...")
            break
    
    return