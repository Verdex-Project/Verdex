from models import *
from main import *
DI.setup()
FireConn.connect()
FireAuth.connect()
emailregex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
def createUser():
    while True:
        username = input("Enter the username of the admin: ")
        if username == "":
            print("Username cannot be empty. Please try again.")
            continue
        break
    while True:
        name = input("Enter the name of the admin: ")
        if name == "":
            print("Name cannot be empty. Please try again.")
            continue
        break
    for accountID in DI.data['accounts']:
        if DI.data['accounts'][accountID]['username'] == username:
            print("Username already exists. Please try again.")
            return
        if DI.data['accounts'][accountID]['name'] == name:
            print("Name already exists. Please try again.")
            return
    while True:
        email = input("Enter the email of the admin: ")
        if email == "":
            print("Email cannot be empty. Please try again.")
            continue
        elif not re.fullmatch(emailregex, email):
            print("Invalid email. Please try again.")
            continue
        break
    while True:
        position = input("Enter the position of the admin: ")
        if position == "":
            print("Position cannot be empty. Please try again.")
            continue
        break
    while True:
        password = input("Enter the password of the admin: ")
        if password == "":
            print("Password cannot be empty. Please try again.")
            continue
        elif len(password)<6:
            print("Password must be at least 6 characters long. Please try again.")
            continue
        break
    accID = Universal.generateUniqueID()
    responseObject =FireAuth.createUser(email, password)
    DI.data['accounts'][accID] = {
            'id': accID,
            "fireAuthID": responseObject['uid'],
            "username": username,
            "email": email,
            "idToken": responseObject['idToken'],
            "refreshToken": responseObject['refreshToken'],
            'tokenExpiry': (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat),
            'disabled': False,
            'admin': True,
            'forumBanStatus': False,
            'name': name,
            "position": position
    }
    Logger.log("ADMINCONSOLE CREATEUSER: Created admin user with username {} and email {}".format(username, email))
    DI.save()
while True:
    print("""
--------------------------------
Welcome to Verdex Admin Console
--------------------------------
Select an option:
1. Add a new admin user
2. Change name of an admin user
3. Change position of an adomin user
4. Downgrade an admin user to a normal user
5. Delete an admin user
6. Exit
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
        username = input("Enter the username of the admin: ")
    elif choice == 3:
        username = input("Enter the username of the admin: ")
    elif choice == 4:
        username = input("Enter the username of the admin: ")
    elif choice == 5:
        username = input("Enter the username of the admin: ")
    elif choice == 6:
        break
    else:
        print("Invalid choice. Please try again.")
        continue
