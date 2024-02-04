from models import *

FireAuth.connect()
FireConn.connect()

input("Do you want to reset all Firebase data? (Press Enter to continue) ")
print("Resetting...")

for fireUser in FireAuth.listUsers():
    FireAuth.deleteAccount(fireUser.uid, admin=True)

FireRTDB.setRef({})