import re, datetime, sys, copy
from models import DI, Logger, Universal, Encryption
from addons import FireConn, FireAuth
from emailer import Emailer
from getpass import getpass
print("Setting up .....")

## Set up FireConn
if FireConn.checkPermissions():
    response = FireConn.connect()
    if response != True:
        print("ADMINCONSOLE: Error in setting up FireConn; error: " + response)
        sys.exit(1)
else:
    print("Firebase admin connection not established due to insufficient permissions.")

# # Setup DI
response = DI.setup()
if response != "Success":
    print("ADMINCONSOLE: Error in setting up DI; error: " + response)
    sys.exit(1)

response = FireAuth.connect()
if not response:
    print(f"ADMINCONSOLE: Failed to establish FireAuth connection. Response: {response}")
    sys.exit(1)

if FireConn.checkPermissions():
    previousCopy = copy.deepcopy(DI.data["accounts"])
    DI.data["accounts"] = FireAuth.generateAccountsObject(fireAuthUsers=FireAuth.listUsers(), existingAccounts=DI.data["accounts"], strategy="overwrite")
    DI.save()

    if previousCopy != DI.data["accounts"]:
        print("ADMINCONSOLE: Necessary database synchronisation with Firebase Authentication complete.")

Emailer.checkContext()
emailregex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


def checkUsername(username):
    for accountID in DI.data['accounts']:
        if DI.data['accounts'][accountID]['username'] == username:
            print("Username already exists. Please try again.")
            return True
    return False
def createUser():
    while True:
        username = input("Enter the username of the admin: ").strip()
        if username == "":
            print("Username cannot be empty. Please try again.")
            continue
        elif checkUsername(username):
            continue
        break

    while True:
        password = getpass("Enter the password of the admin: ").strip()
        if password == "":
            print("Password cannot be empty. Please try again.")
            continue
        elif len(password)<6:
            print("Password must be at least 6 characters long. Please try again.")
            continue
        break
    while True:
        email = input("Enter the email of the admin: ").strip()
        if email == "":
            print("Email cannot be empty. Please try again.")
            continue
        elif not re.fullmatch(emailregex, email):
            print("Invalid email. Please try again.")
            continue
        break

    while True:
        name = input("Enter the name of the admin: ").strip()
        if name == "":
            print("Name cannot be empty. Please try again.")
            continue
        break

    while True:
        position = input("Enter the position of the admin: ").strip()
        if position == "":
            print("Position cannot be empty. Please try again.")
            continue
        break
    
    accID = Universal.generateUniqueID()
    responseObject =FireAuth.createUser(email, password)
    DI.data['accounts'][accID] = {
            'id': accID,
            "fireAuthID": responseObject['uid'],
            "username": username,
            "email": email,
            "password": Encryption.encodeToSHA256(password),
            "idToken": responseObject['idToken'],
            "refreshToken": responseObject['refreshToken'],
            'tokenExpiry': (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat),
            'disabled': False,
            'admin': True,
            'name': name,
            "position": position
    }
    Logger.log("ADMINCONSOLE CREATEUSER: Created admin user with username {} and email {}".format(username, email))
    DI.save()
    Emailer.sendEmail(email, 'Welcome to Verdex Admin', 'Dear recipients, you have an account that is recognised as a Verdex Admin. Please use your registered username and email to login into the Admin dashboard', '<h1>Dear User, you have an account that is recognised as a Verdex Admin. Please use your registered username and email to login into the Admin dashboard</h1>')
def changeName(userName):
    if userName == "":
        print("Username cannot be empty. Please try again.")
        return

    for accountID in DI.data['accounts']:
        if DI.data['accounts'][accountID]['username'] == userName:
            if DI.data['accounts'][accountID]['admin'] == False:
                print("User with username {} is not an admin. Please try again.".format(userName))
                return
            while True:
                newName = input("Enter the new name of the admin: ")
                if newName == "":
                    print("Name cannot be empty. Please try again.")
                    continue
                break

            DI.data['accounts'][accountID]['name'] = newName
            Logger.log("ADMINCONSOLE CHANGENAME: Changed name of admin user with username {}".format(userName))
            DI.save()
            return

    print("Admin user with username {} not found.".format(userName))
            
def changePosition(userName):
    if userName == "":
        print("Username cannot be empty. Please try again.")
        return

    for accountID in DI.data['accounts']:
        if DI.data['accounts'][accountID]['username'] == userName:
            if DI.data['accounts'][accountID]['admin'] == False:
                print("User with username {} is not an admin. Please try again.".format(userName))
                return
            while True:
                newPosition = input("Enter the new position of the admin: ")
                if newPosition == "":
                    print("Position cannot be empty. Please try again.")
                    continue
                break

            DI.data['accounts'][accountID]['position'] = newPosition
            Logger.log("ADMINCONSOLE CHANGEPOSITION: Changed position of admin user with username {}".format(userName))
            DI.save()
            return

    print("Admin user with username {} not found.".format(userName))

def downgradeAdmin(userName):
    if userName == "":
        print("Username cannot be empty. Please try again.")
        return

    for accountID in DI.data['accounts']:
        if DI.data['accounts'][accountID]['username'] == userName:
            if not DI.data['accounts'][accountID]['admin']:
                print("User with username {} is not an admin. Please try again.".format(userName))
                return

            DI.data['accounts'][accountID]['admin'] = False
            Logger.log("ADMINCONSOLE DOWNGRADEADMIN: Downgraded admin user with username {}".format(userName))
            DI.save()
            return

    print("Admin user with username {} not found.".format(userName))

def deleteUser(userName):
    if userName == "":
        print("Username cannot be empty. Please try again.")
        return

    for accountID in DI.data['accounts']:
        if DI.data['accounts'][accountID]['username'] == userName:
            if not DI.data['accounts'][accountID]['admin']:
                print("User with username {} is not an admin. Please try again.".format(userName))
                return

            FireAuth.deleteAccount(DI.data['accounts'][accountID]['fireAuthID'], admin=True)
            del DI.data['accounts'][accountID]
            Logger.log("ADMINCONSOLE DELETEUSER: Deleted admin user with username {}".format(userName))
            DI.save()
            return
        
    print("Admin user with username {} not found.".format(userName))
            
while True:
    print("""
--------------------------------
Welcome to Verdex Admin Console
--------------------------------
Select an option:
1. Add a new admin user
2. Change name or position of an admin user
3. Downgrade an admin user to a normal user
4. Delete an admin user
0. Exit
--------------------------------
          """)
    try:
        choice = int(input("Enter your choice: "))
    except:
        print("Invalid choice. Please try again.")
        continue

    if choice == 1:
        createUser()
    
    elif choice == 2:
        try:
            choice = int(input("Enter 1 to change name or 2 to change position: "))
        except:
            print("Invalid choice. Please try again.")
            continue
        username = input("Enter the username of the admin: ")
        if choice == 1:
            changeName(username)
        elif choice == 2:
            changePosition(username)
        else:
            print("Invalid choice. Please try again.")
            continue

    elif choice == 3:
        username = input("Enter the username of the admin: ")
        downgradeAdmin(username)

    elif choice == 4:
        username = input("Enter the username of the admin: ")
        deleteUser(username)

    elif choice == 0:
        break
    else:
        print("Invalid choice. Please try again.")
        continue
