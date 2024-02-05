from models import *
import shutil

FireAuth.connect()
FireConn.connect()

choice = input("Do you want to reset all Firebase data or wipe all local persistent files? (1/2) ")
print("Resetting...")

if choice == "1":
    for fireUser in FireAuth.listUsers():
        FireAuth.deleteAccount(fireUser.uid, admin=True)

    FireRTDB.setRef({})
elif choice == "2":
    for file in ["config.txt", "database.txt", "analytics.json"]:
        if os.path.isfile(file):
            os.remove(file)
        
    for folder in ["UserFolders", "reports"]:
        if os.path.isdir(folder):
            shutil.rmtree(folder)

print("Done.")