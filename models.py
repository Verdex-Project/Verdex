import os, json, sys, random, datetime, copy, base64
from passlib.hash import sha256_crypt as sha
from dotenv import load_dotenv
load_dotenv()

def fileContent(filePath, passAPIKey=False):
    with open(filePath, 'r') as f:
        f_content = f.read()
        if passAPIKey:
            f_content = f_content.replace("\{{ API_KEY }}", os.getenv("API_KEY"))
        return f_content
    
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