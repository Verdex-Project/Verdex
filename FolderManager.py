import os, shutil

class FolderManager:
    tldName = "UserFolders"

    @staticmethod
    def setup():
        if not os.path.isdir(os.path.join(os.getcwd(), FolderManager.tldName)):
            try:
                os.mkdir(os.path.join(os.getcwd(), FolderManager.tldName))
            except Exception as e:
                return "ERROR: Failed to create top-level directory; error: {}".format(e)
        return "Success"

    @staticmethod
    def registerFolder(accID):
        if os.path.isdir(os.path.join(os.getcwd(), FolderManager.tldName, accID)):
            return True
        
        try:
            os.mkdir(os.path.join(os.getcwd(), FolderManager.tldName, accID))
            print("FM: Registered folder for account {}".format(accID))
        except Exception as e:
            return "ERROR: Failed to register folder; error: {}".format(e)
        
        return True

    @staticmethod
    def checkIfFolderIsRegistered(accID):
        if os.path.isdir(os.path.join(os.getcwd(), FolderManager.tldName, accID)):
            return True
        else:
            return False

    @staticmethod
    def deleteFolder(accID):
        if os.path.isdir(os.path.join(os.getcwd(), FolderManager.tldName, accID)):
            try:
                shutil.rmtree(os.path.join(os.getcwd(), FolderManager.tldName, accID), ignore_errors=True)
                return True
            except Exception as e:
                return "ERROR: Failed to delete folder; error: {}".format(e)
        else:
            return "ERROR: No such folder registered."

    @staticmethod
    def getFilenames(accID):
        if os.path.isdir(os.path.join(os.getcwd(), FolderManager.tldName, accID)):
            filenames = [f for f in os.listdir(os.path.join(os.getcwd(), FolderManager.tldName, accID)) if os.path.isfile(os.path.join(os.getcwd(), FolderManager.tldName, accID, f))]
            if filenames == []:
                filenames = []
            return filenames
        else:
            return "ERROR: No such folder exists."

    @staticmethod
    def deleteFile(accID, filename):
        if os.path.isdir(os.path.join(os.getcwd(), FolderManager.tldName, accID)):
            if os.path.isfile(os.path.join(os.getcwd(), FolderManager.tldName, accID, filename)):
                try:
                    os.remove(os.path.join(os.getcwd(), FolderManager.tldName, accID, filename))
                    return True
                except Exception as e:
                    return "ERROR: An unknown error occured in deleting the file."
            else:
                return "ERROR: No such file exists in the folder registered under that account ID."
        else:
            return "ERROR: No such folder exists."
        
    @staticmethod
    def getFileExtension(filename):
        extension = ''
        for char in reversed(filename):
            if char == '.':
                break
            else:
                extension = char + extension
        
        return extension