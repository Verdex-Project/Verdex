import os, shutil
from main import Logger

class FolderManager :
    
    @staticmethod
    def registerFolder(username):
        if os.path.isdir(os.path.join(os.getcwd(), username, f"{username}.pfp.png")):
            return FolderManager .folderAlreadyRegistered
        
        try:
            os.mkdir(os.path.join(os.getcwd(), username, f"{username}.pfp.png"))
            Logger.log("ACCOUNTS FOLDERMANAGER REGISTERFOLDER: User {} registered a PFP folder.".format(username))
        except Exception as e:
            Logger.log("ACCOUNTS FOLDERMANAGER REGISTERFOLDER ERROR: {}".format(e))
            return FolderManager .unknownError
        return "PFP Folder for {} registered.".format(username)

    @staticmethod
    def checkIfFolderIsRegistered(username):
        if os.path.isdir(os.path.join(os.getcwd(), username, f"{username}.pfp.png")):
            return True
        else:
            return False

    @staticmethod
    def deleteFolder(username):

        if os.path.isdir(os.path.join(os.getcwd(), username, f"{username}.pfp.png")):
            try:
                shutil.rmtree(os.path.join(os.getcwd(), username, f"{username}.pfp.png"), ignore_errors=True)
                return True
            except Exception as e:
                Logger.log("ACCOUNTS FOLDERMANAGER DELETEFOLDER ERROR: {}".format(e))
                return FolderManager .unknownError
        else:
            return FolderManager .folderDoesNotExist

    @staticmethod
    def getFilenames(username):
        if os.path.isdir(os.path.join(os.getcwd(), username, f"{username}.pfp.png")):
            filenames = [f for f in os.listdir(os.path.join(os.getcwd(), username, f"{username}.pfp.png")) if os.path.isfile(os.path.join(os.path.join(os.getcwd(), username, f"{username}.pfp.png"), f))]
            if filenames == []:
                filenames = []
            return filenames
        else:
            return FolderManager .folderDoesNotExist

    @staticmethod
    def deleteFile(username, filename):
        if os.path.isdir(os.path.join(os.getcwd(), username, f"{username}.pfp.png")):
            if os.path.isfile(os.path.join(os.getcwd(), username, f"{username}.pfp.png")):
                try:
                    os.remove(os.path.join(os.getcwd(), username, f"{username}.pfp.png"))
                    return "FM: Successfully deleted the file."
                except Exception as e:
                    Logger.log("ACCOUNTS FOLDERMANAGER DELETEFILE ERROR: Failed to delete {} of {}: {}".format(filename, username, e))
                    return FolderManager .deleteFileError
            else:
                return FolderManager .fileDoesNotExist
        else:
            return FolderManager .folderDoesNotExist



class FolderManager (Exception):
    def __init__(self, message):
        self.message = message

    folderAlreadyRegistered = "FM: The folder is already registered for the username."
    unknownError = "FM: There was an unknown error in performing the action. Check console for more information."
    folderDoesNotExist = "FM: No such folder exists."
    deleteFileError = "FM: An unknown error occured in deleting the file. Check console for more information."
    fileDoesNotExist = "FM: No such file exists in the folder registered under that username."

    @staticmethod
    def checkIfErrorMessage(msg):
        msgsArray = [
            FolderManager .folderAlreadyRegistered,
            FolderManager .unknownError,
            FolderManager .folderDoesNotExist,
            FolderManager .deleteFileError,
            FolderManager .fileDoesNotExist
        ]
        
        if msg in msgsArray:
            return True
        else:
            return False