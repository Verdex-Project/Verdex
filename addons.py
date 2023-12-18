import os, sys, json, datetime, copy
import firebase_admin
from firebase_admin import db
from dotenv import load_dotenv
load_dotenv()

class AddonsManager:
    config = None

    @staticmethod
    def setup():
        try:
            if not os.path.isfile(os.path.join(os.getcwd(), 'config.txt')):
                with open('config.txt', 'w') as f:
                    f.write("{}")
            
            AddonsManager.config = json.load(open('config.txt', 'r'))
            return "Success"
        except Exception as e:
            return "ERROR: Failed to check for config file and create a new one if there isn't one; error: {}".format(e)

    @staticmethod
    def setConfigKey(keyName, value):
        try:
            AddonsManager.config[keyName] = value
            json.dump(AddonsManager.config, open('config.txt', 'w'))
            return "Success"
        except Exception as e:
            return "ERROR: Failed to set config key; error: {}".format(e)

    @staticmethod
    def readConfigKey(keyName):
        try:
            if keyName not in AddonsManager.config:
                return "Key Not Found"
            return AddonsManager.config[keyName]
        except Exception as e:
            return "ERROR: Failed to read config key; error: {}".format(e)
    
    @staticmethod
    def deleteConfigKey(keyName):
        try:
            if keyName not in AddonsManager.config:
                return "Key Not Found"
            del AddonsManager.config[keyName]
            json.dump(AddonsManager.config, open('config.txt', 'w'))
        except Exception as e:
            return "ERROR: Failed to delete config key; error: {}".format(e)