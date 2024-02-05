import re, datetime, sys, copy
from models import DI, Logger, Universal, Encryption, fileContent, customRenderTemplate
from addons import FireConn, FireAuth, AddonsManager
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

response = AddonsManager.setup()
if response != "Success":
    print("ADMINCONSOLE: Error in setting up AddonsManager; error: " + response)
    sys.exit(1)
else:
    print("ADDONSMANAGER: Setup complete.")

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
        email = input("Enter the email of the admin: ").strip()
        if email == "":
            print("Email cannot be empty. Please try again.")
            continue
        elif not re.fullmatch(emailregex, email):
            print("Invalid email. Please try again.")
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
    
    print()
    print("Creating admin account on Firebase Authentication...")
    accID = Universal.generateUniqueID()
    responseObject =FireAuth.createUser(email, password)
    if "ERROR" in responseObject:
        print("Failed to create admin account on Firebase Authentication. Error: {}".format(responseObject))
        return

    print()
    print("Creating admin account on database...")
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
    DI.save()

    Logger.log("ADMINCONSOLE CREATEUSER: Created admin user with username {} and email {}".format(username, email), debugPrintExplicitDeny=True)

    print()
    print("Sending welcome email to admin...")
    altText =f'''
    Dear {DI.data['accounts'][accID]['name']},

    Welcome to Verdex Family!

    We are pleased to have you on board.

    Kindly regards, The Verdex Team
    THIS IS AN AUTOMATED MESSAGE DELIVERED TO YOU BY VERDEX. DO NOT REPLY TO THIS EMAIL.
    {Universal.copyright}
    '''
    html = customRenderTemplate(
        'templates/emails/createAdminAccountEmail.html'
        , name=DI.data['accounts'][accID]['name']
        , copyright = Universal.copyright
        )
    Emailer.sendEmail(email, 'Welcome to Verdex Admin!', altText, html)
    print()
    print("Admin account created successfully!")

    return


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
            print()
            print('Changing name of the admin user on local database...')
            DI.data['accounts'][accountID]['name'] = newName
            DI.save()

            Logger.log("ADMINCONSOLE CHANGENAME: Changed name of admin user with username {}".format(userName), debugPrintExplicitDeny=True)
            print()
            print('Admin Account change name success')
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
            print()
            print(f'Changing position of admin user...')
            DI.data['accounts'][accountID]['position'] = newPosition
            DI.save()
            Logger.log("ADMINCONSOLE CHANGEPOSITION: Changed position of admin user with username {}".format(userName), debugPrintExplicitDeny=True)
            print()
            print('Admin Account change position success')
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
            print()
            print('Downgrading Admin Account...')
            DI.data['accounts'][accountID]['admin'] = False
            DI.save()

            Logger.log("ADMINCONSOLE DOWNGRADEADMIN: Downgraded admin user with username {}".format(userName), debugPrintExplicitDeny=True)
            print()
            print('Admin Account successfully downgraded')
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
            print("Deleting admin account on Firebase Authentication...")
            response = FireAuth.deleteAccount(DI.data['accounts'][accountID]['fireAuthID'], admin=True)
            if isinstance(response, str):
                Logger.log(f"ADMINCONSOLE DELETEUSER ERROR: Failed to delete user from Firebase Authentication. Response: {response}", debugPrintExplicitDeny=True)
                print(f"Failed to delete user from Firebase Authentication. Response: {response}")
                return
            print()
            print('Admin Account deleted successfully on Firebase Authentication...')
            print()
            print('Deleting admin account on local database...')
            del DI.data['accounts'][accountID]
            print()
            print('Admin Account deleted successfully on local database...')
            DI.save()

            Logger.log("ADMINCONSOLE DELETEUSER: Deleted admin user with username {}".format(userName), debugPrintExplicitDeny=True)
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
