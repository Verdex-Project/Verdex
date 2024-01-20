import os, shutil

class FolderManager :
    
    @staticmethod
    def registerFolder(accID):
        if os.path.isdir(os.path.join(os.getcwd(), "UserFolders", "{}pfp.png".format(accID))):
            # use accountid instead, remove .pfp => pfp "UserFolders", remove space, remove logging, return errors / bool
            # Path of a specific user folder: os.path.join(os.getcwd(), "UserFolders", {ACCOUTNIDHERE})
            # Path of a pfp file in a specific user folder: os.path.join(os.getcwd(), "UserFolders", {ACCOUNTIDHERE}, "{ACCOUNTIDHERE}pfp.?")
            return "FMERROR: The folder is already registered."
        
        try:
            os.mkdir(os.path.join(os.getcwd(), "UserFolders", "{}pfp.png".format(accID)))
            print("FM: Registered folder for account {}".format(accID))
        except Exception as e:
            print("FMERROR: {}".format(e))
            return "FMERROR: There was an unknown error in performing the action."
        
        return "FMSUCCESS: Folder registered."

    @staticmethod
    def checkIfFolderIsRegistered(accID):
        if os.path.isdir(os.path.join(os.getcwd(), "UserFolders", "{}pfp.png".format(accID))):
            return True
        else:
            return False

    @staticmethod
    def deleteFolder(accID):

        if os.path.isdir(os.path.join(os.getcwd(), "UserFolders", "{}pfp.png".format(accID))):
            try:
                shutil.rmtree(os.path.join(os.getcwd(), "UserFolders", "{}pfp.png".format(accID)), ignore_errors=True)
                return True
            except Exception as e:
                print("FMERROR: {}".format(e))
                return "FMERROR: There was an unknown error in performing the action."
        else:
            return "FMERROR: No such folder registered."

    @staticmethod
    def getFilenames(accID):
        if os.path.isdir(os.path.join(os.getcwd(), "UserFolders", "{}pfp.png".format(accID))):
            filenames = [f for f in os.listdir(os.path.join(os.getcwd(), "UserFolders", "{}pfp.png".format(accID))) if os.path.isfile(os.path.join(os.path.join(os.getcwd(), "UserFolders", "{}pfp.png".format(accID)), f))]
            if filenames == []:
                filenames = []
            return filenames
        else:
            return "FMERROR: No such folder exists."

    @staticmethod
    def deleteFile(accID, filename):
        if os.path.isdir(os.path.join(os.getcwd(), "UserFolders", "{}pfp.png".format(accID))):
            if os.path.isfile(os.path.join(os.getcwd(), "UserFolders", "{}pfp.png".format(accID), filename)):
                try:
                    os.remove(os.path.join(os.getcwd(), "UserFolders", "{}pfp.png".format(accID), filename))
                    return "FMSUCCESS: Successfully deleted the file."
                except Exception as e:
                    print("FMERROR: {}".format(e))
                    return "FMERROR: An unknown error occured in deleting the file."
            else:
                return "FMERROR: No such file exists in the folder registered under that username."
        else:
            return "FMERROR: No such folder exists."