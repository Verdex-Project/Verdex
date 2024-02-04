import json, random, time, sys, subprocess, os, shutil, copy, requests, datetime
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint, send_file, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from models import *
from FolderManager import FolderManager
from emailer import Emailer
from analytics import Analytics
from GMapsService import GoogleMapsService
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

## Configure app
UPLOAD_FOLDER = os.path.join(os.getcwd(), "Chute")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ['AppSecretKey']

## Global methods
def deleteSession(accountID):
    if accountID not in DI.data["accounts"]:
        return False
    
    if "idToken" in DI.data["accounts"][accountID]:
        del DI.data["accounts"][accountID]["idToken"]
    if "refreshToken" in DI.data["accounts"][accountID]:
        del DI.data["accounts"][accountID]["refreshToken"]
    if "tokenExpiry" in DI.data["accounts"][accountID]:
        del DI.data["accounts"][accountID]["tokenExpiry"]
    DI.save()

    session.clear()

    return True

def manageIDToken(checkIfAdmin=False):
    '''Returns account ID if token is valid (will refresh if expiring soon) and a str error message if not valid.'''

    if "idToken" not in session:
        return "ERROR: Please sign in first."
    
    for accountID in DI.data["accounts"]:
        if "idToken" not in DI.data["accounts"][accountID]:
            # This account doesn't have an ID token, so
            continue
        elif DI.data["accounts"][accountID]["idToken"] == session["idToken"]:
            delta = datetime.datetime.strptime(DI.data["accounts"][accountID]["tokenExpiry"], Universal.systemWideStringDatetimeFormat) - datetime.datetime.now()
            if delta.total_seconds() < 0:
                deleteSession(accountID)
                Logger.log("MANAGEIDTOKEN: Session expired for account with ID '{}'.".format(accountID))
                return "ERROR: Your session has expired. Please sign in again."
            elif delta.total_seconds() < 600:
                # Refresh token if it's less than 10 minutes from expiring
                response = FireAuth.refreshToken(DI.data["accounts"][accountID]["refreshToken"])
                if isinstance(response, str):
                    # Refresh token is invalid, delete session entirely
                    deleteSession(accountID)
                    return "ERROR: Your session expired. Please sign in again."
                
                DI.data["accounts"][accountID]["idToken"] = response["idToken"]
                DI.data["accounts"][accountID]["refreshToken"] = response["refreshToken"]
                DI.data["accounts"][accountID]["tokenExpiry"] = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat)
                DI.save()

                Logger.log("MANAGEIDTOKEN: Refreshed token for account with ID '{}'.".format(accountID))

                session["idToken"] = response["idToken"]

            if checkIfAdmin:
                if not ("admin" in DI.data["accounts"][accountID] and DI.data["accounts"][accountID]["admin"] == True):
                    return "ERROR: Access forbidden due to insufficient permissions."

            return "SUCCESS: {}".format(accountID)
    
    # If we get here, the session is invalid as the ID token is not in the database
    session.clear()
    return "ERROR: Invalid credentials."

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def updateAnalytics():
    Analytics.add_metrics(Analytics.EventTypes.get_request if request.method == "GET" else Analytics.EventTypes.post_request)
    return

@app.route('/')
def homepage():
    if "generateReport" in request.args and request.args["generateReport"] == "true":
        Analytics.generateReport()

    return render_template('homepage.html')

# Security pages
@app.route('/security/error')
def error():
    if 'error' not in request.args:
        return render_template("error.html", error=None, originURL=request.host_url)
    else:
        return render_template("error.html", error=request.args["error"], originURL=request.host_url)
    
@app.route("/security/unauthorised")
def unauthorised():
    if "error" not in request.args:
        return render_template("unauthorised.html", message="No error message was provided.", originURL=request.host_url)
    return render_template("unauthorised.html", message=request.args["error"], originURL=request.host_url)

## Make a 404 route
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error="404: Page not found.", originURL=request.host_url)

if __name__ == '__main__':
    # Boot pre-processing

    ## Set up FireConn
    if FireConn.checkPermissions():
        response = FireConn.connect()
        if response != True:
            print("MAIN BOOT: Error in setting up FireConn; error: " + response)
            sys.exit(1)
        else:
            print("FIRECONN: Firebase connection established.")

    ## Set up DatabaseInterface
    response = DI.setup()
    if response != "Success":
        print("MAIN BOOT: Error in setting up DI; error: " + response)
        sys.exit(1)
    else:
        print("DI: Setup complete.")

    ## Set up AddonsManager
    response = AddonsManager.setup()
    if response != "Success":
        print("MAIN BOOT: Error in setting up AddonsManager; error: " + response)
        sys.exit(1)
    else:
        print("ADDONSMANAGER: Setup complete.")

    ## Set up FireAuth
    response = FireAuth.connect()
    if not response:
        print("MAIN BOOT: Failed to establish FireAuth connection. Boot aborted.")
        sys.exit(1)
    else:
        print("FIREAUTH: Setup complete.")

    ## Set up FolderManager
    response = FolderManager.setup()
    if response != "Success":
        print("MAIN BOOT: Error in setting up FolderManager; error: " + response)
        sys.exit(1)

    ## Get Emailer to check context
    Emailer.checkContext()
    if Emailer.servicesEnabled and AddonsManager.readConfigKey("EmailingServicesEnabled") == False:
        Emailer.servicesEnabled = False

    ## Set up GoogleMapsService
    GoogleMapsService.checkContext()
    
    ## Set up Analytics
    if AddonsManager.readConfigKey("AnalyticsEnabled") != "Key Not Found":
        Analytics.setup(adminEnabled=AddonsManager.readConfigKey("AnalyticsEnabled"))
    else:
        Analytics.setup()
        AddonsManager.setConfigKey("AnalyticsEnabled", Analytics.adminEnabled)
    
    ## Set up Logger
    Logger.setup()

    ## Load generation data from file
    Universal.loadGenerationData()

    # Database Synchronisation with Firebase Auth accounts
    if FireConn.checkPermissions():
        previousCopy = copy.deepcopy(DI.data["accounts"])
        DI.data["accounts"] = FireAuth.generateAccountsObject(fireAuthUsers=FireAuth.listUsers(), existingAccounts=DI.data["accounts"], strategy="overwrite")
        DI.save()

        if previousCopy != DI.data["accounts"]:
            print("MAIN: Necessary database synchronisation with Firebase Authentication complete.")
    
    if 'DebugMode' in os.environ and os.environ['DebugMode'] == 'True':
        DI.data["itineraries"] = {
            "abc123": {
                "title" : "My Itinerary",
                "description" : "3 days itinerary in Singapore",
                "generationDateTime" : datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat),
                "associatedAccountID": "366e25aff98845f28f284434b739b6b1",
                "days" : {
                    "1" : {
                        "date" : "2024-03-01",
                        "activities" : {
                            "0" : {
                                "name" : "Marina Bay Sands",
                                "activity" : "Singapore",
                                "imageURL" : "https://mustsharenews.com/wp-content/uploads/2023/03/MBS-Expansion-Delay-FI.jpg",
                                "startTime" : "0800",
                                "endTime" : "1000"
                            },
                            "1" : {
                                "name" : "Universal Studios Singapore",
                                "activity" : "Singapore",
                                "imageURL" : "https://static.honeykidsasia.com/wp-content/uploads/2021/02/universal-studios-singapore-kids-family-guide-honeykids-asia-900x643.jpg",
                                "startTime" : "1000", 
                                "endTime" : "1800"
                            },
                            "2" : {
                                "name" : "Sentosa Island",
                                "activity" : "Singapore",
                                "imageURL" : "https://upload.wikimedia.org/wikipedia/commons/0/0f/Merlion_Sentosa.jpg",
                                "startTime" : "1800",
                                "endTime" : "2200"
                            }
                        }
                    },
                    "2" : {
                        "date" : "2024-03-02",
                        "activities" : {
                            "0" : {
                                "name" : "SEA Aquarium",
                                "activity" : "Singapore",
                                "imageURL" : "https://image.kkday.com/v2/image/get/h_650%2Cc_fit/s1.kkday.com/product_23301/20230323024107_wG7zu/jpg",
                                "startTime" : "0800",
                                "endTime" : "1200"
                            },
                            "1" : {
                                "name" : "Singapore Botanic Gardens",
                                "activity" : "Singapore",
                                "imageURL" : "https://www.nparks.gov.sg/-/media/nparks-real-content/gardens-parks-and-nature/sg-botanic-gardens/sbg10_047alt.ashx",
                                "startTime" : "1200",
                                "endTime" : "1600"
                            },
                            "2" : {
                                "name" : "Orchard Road",
                                "activity" : "Singapore",
                                "imageURL": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Presenting..._the_real_ION_%288200217734%29.jpg/1024px-Presenting..._the_real_ION_%288200217734%29.jpg",
                                "startTime" : "1600",
                                "endTime" : "2200"
                            }
                        }
                    },
                    "3" : {
                        "date" : "2024-03-03",
                        "activities" : {
                            "0" : {
                                "name" : "Gardens by the Bay",
                                "activity" : "Singapore",
                                "imageURL" : "https://afar.brightspotcdn.com/dims4/default/ada5ead/2147483647/strip/true/crop/728x500+36+0/resize/660x453!/quality/90/?url=https%3A%2F%2Fafar-media-production-web.s3.us-west-2.amazonaws.com%2Fbrightspot%2F94%2F46%2F4e15fcdc545829ae3dc5a9104f0a%2Foriginal-7d0d74d7c60b72c7e76799a30334803e.jpg",
                                "startTime" : "1000",
                                "endTime" : "1800"
                            },
                            "1" : {
                                "name" : "Chinatown MRT Station",
                                "activity" : "Singapore",
                                "imageURL" : "https://www.tripsavvy.com/thmb/bikgORwUriJhkcbmyRAbEsl_thQ=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/2_chinatown_street_market-5c459281c9e77c00018d54a2.jpg",
                                "startTime" : "1800",
                                "endTime" : "2100"
                            }
                        }
                    }
                }
            },
            "def456": {
                "title" : "Second Itinerary",
                "description" : "5 days itinerary in Singapore",
                "generationDateTime" : datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat),
                "associatedAccountID": "1e80d6b46ac5463390b585ea2f2c00c6",
                "days" : {
                    "1" : {
                        "date" : "2024-04-01",
                        "activities" : {
                            "0" : {
                                "name" : "Marina Bay Sands",
                                "activity" : "Singapore",
                                "imageURL" : "https://mustsharenews.com/wp-content/uploads/2023/03/MBS-Expansion-Delay-FI.jpg",
                                "startTime" : "0800",
                                "endTime" : "1000"
                            },
                            "1" : {
                                "name" : "Universal Studios Singapore",
                                "activity" : "Singapore",
                                "imageURL" : "https://static.honeykidsasia.com/wp-content/uploads/2021/02/universal-studios-singapore-kids-family-guide-honeykids-asia-900x643.jpg",
                                "startTime" : "1000", 
                                "endTime" : "1800"
                            },
                            "2" : {
                                "name" : "Sentosa Island",
                                "activity" : "Singapore",
                                "imageURL" : "https://upload.wikimedia.org/wikipedia/commons/0/0f/Merlion_Sentosa.jpg",
                                "startTime" : "1800",
                                "endTime" : "2200"
                            }
                        }
                    },
                    "2" : {
                        "date" : "2024-04-02",
                        "activities" : {
                            "0" : {
                                "name" : "SEA Aquarium",
                                "activity" : "Singapore",
                                "imageURL" : "https://image.kkday.com/v2/image/get/h_650%2Cc_fit/s1.kkday.com/product_23301/20230323024107_wG7zu/jpg",
                                "startTime" : "0800",
                                "endTime" : "1200"
                            },
                            "1" : {
                                "name" : "Singapore Botanical Gardens",
                                "activity" : "Singapore",
                                "imageURL" : "https://www.nparks.gov.sg/-/media/nparks-real-content/gardens-parks-and-nature/sg-botanic-gardens/sbg10_047alt.ashx",
                                "startTime" : "1200",
                                "endTime" : "1600"
                            },
                            "2" : {
                                "name" : "Orchard Road",
                                "activity" : "Singapore",
                                "imageURL": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Presenting..._the_real_ION_%288200217734%29.jpg/1024px-Presenting..._the_real_ION_%288200217734%29.jpg",
                                "startTime" : "1600",
                                "endTime" : "2200"
                            }
                        }
                    },
                    "3" : {
                        "date" : "2024-04-03",
                        "activities" : {
                            "0" : {
                                "name" : "Gardens by the Bay",
                                "activity" : "Singapore",
                                "imageURL" : "https://afar.brightspotcdn.com/dims4/default/ada5ead/2147483647/strip/true/crop/728x500+36+0/resize/660x453!/quality/90/?url=https%3A%2F%2Fafar-media-production-web.s3.us-west-2.amazonaws.com%2Fbrightspot%2F94%2F46%2F4e15fcdc545829ae3dc5a9104f0a%2Foriginal-7d0d74d7c60b72c7e76799a30334803e.jpg",
                                "startTime" : "1000",
                                "endTime" : "1800"
                            },
                            "1" : {
                                "name" : "Chinatown MRT Station",
                                "activity" : "Singapore",
                                "imageURL" : "https://www.tripsavvy.com/thmb/bikgORwUriJhkcbmyRAbEsl_thQ=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/2_chinatown_street_market-5c459281c9e77c00018d54a2.jpg",
                                "startTime" : "1800",
                                "endTime" : "2100"
                            }
                        }
                    }
                }
            }
        }
        DI.save()
        print("Sample itinerary Set!")

    # Register routes
    
    ## Generation routes
    ## API routes
    from api import apiBP
    app.register_blueprint(apiBP)

    from generation.itineraryGeneration import itineraryGenBP
    app.register_blueprint(itineraryGenBP)
    
    ## Admin routes
    from admin.contact_form import contactBP
    app.register_blueprint(contactBP)

    from admin.home import adminHomeBP
    app.register_blueprint(adminHomeBP)
    
    ## Forum routes
    from forum.forum import forumBP
    app.register_blueprint(forumBP)

    ## Editor routes
    from editor.editor import editorPage
    app.register_blueprint(editorPage)

    ## Completion routes
    from editor.completion import completionPage
    app.register_blueprint(completionPage)

    ## Account route
    from identity.accounts import accountsBP
    app.register_blueprint(accountsBP)

    ## Assets service
    from assets import assetsBP
    app.register_blueprint(assetsBP)

    print()
    print("All services online; boot pre-processing and setup complete.")
    print("Booting Verdex...")

    app.run(port=8000, host='0.0.0.0')