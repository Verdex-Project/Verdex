import json, random, time, sys, subprocess, os, shutil, copy, requests, datetime
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint, send_file, session
from flask_cors import CORS
from models import *
from dotenv import load_dotenv
from analytics import Analytics
load_dotenv()

app = Flask(__name__)
CORS(app)

## Configure app
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

    return True

def manageIDToken():
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
                del session["idToken"]
                Logger.log("MANAGEIDTOKEN: Session expired for account with ID '{}'.".format(accountID))
                return "ERROR: Your session has expired. Please sign in again."
            elif delta.total_seconds() < 600:
                # Refresh token if it's less than 10 minutes from expiring
                response = FireAuth.refreshToken(DI.data["accounts"][accountID]["refreshToken"])
                if isinstance(response, str):
                    # Refresh token is invalid, delete session entirely
                    deleteSession(accountID)
                    del session["idToken"]
                    return False
                
                DI.data["accounts"][accountID]["idToken"] = response["idToken"]
                DI.data["accounts"][accountID]["refreshToken"] = response["refreshToken"]
                DI.data["accounts"][accountID]["tokenExpiry"] = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(Universal.systemWideStringDatetimeFormat)
                DI.save()

                Logger.log("MANAGEIDTOKEN: Refreshed token for account with ID '{}'.".format(accountID))

                session["idToken"] = response["idToken"]

            return "SUCCESS: {}".format(accountID)
    
    # If we get here, the session is invalid as the ID token is not in the database
    del session["idToken"]
    return "ERROR: Invalid credentials."

@app.before_request
def updateAnalytics():
    Analytics.add_metrics('get_request' if request.method == "GET" else "post_request")
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
    
    ## Set up Analytics
    Analytics.setup()
    Analytics.load_metrics()
    ## Set up Logger
    Logger.setup()

    # Database Synchronisation with Firebase Auth accounts
    if FireConn.checkPermissions():
        previousCopy = copy.deepcopy(DI.data["accounts"])
        DI.data["accounts"] = FireAuth.generateAccountsObject(fireAuthUsers=FireAuth.listUsers(), existingAccounts=DI.data["accounts"], strategy="overwrite")
        DI.save()

        if previousCopy != DI.data["accounts"]:
            print("MAIN: Necessary database synchronisation with Firebase Authentication complete.")

    # Main branch's original Sample Itinerary Database Structure
    # if 'DebugMode' in os.environ and os.environ['DebugMode'] == 'True':
    #     DI.data["itineraries"] = {
    #         "abc123" : {
    #             "id" : "abc123",
    #             "title" : "My Itinerary",
    #             "description" : "3 days itinerary in Singapore",
    #             "gene`r`ationDateTime" : datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat),
    #             "days" : {
    #                 "1" : {
    #                     "date" : "2024-01-01",
    #                     "activities" : {
    #                         "0" : {
    #                             "name" : "Marina Bay Sands",
    #                             "location" : "Singapore",
    #                             "locationCoordinates" : {"lat" : "123.456", "long" : "321.654"},
    #                             "imageURL" : "https://mustsharenews.com/wp-content/uploads/2023/03/MBS-Expansion-Delay-FI.jpg",
    #                             "startTime" : "0800",
    #                             "endTime" : "1000"
    #                         },
    #                         "1" : {
    #                             "name" : "Universal Studios Singapore",
    #                             "location" : "Singapore",
    #                             "locationCoordinates" : {"lat" : "135.579", "long" : "579.135"},
    #                             "imageURL" : "https://static.honeykidsasia.com/wp-content/uploads/2021/02/universal-studios-singapore-kids-family-guide-honeykids-asia-900x643.jpg",
    #                             "startTime" : "1000", 
    #                             "endTime" : "1800"
    #                         },
    #                         "2" : {
    #                             "name" : "Sentosa",
    #                             "location" : "Singapore",
    #                             "locationCoordinates" : {"lat" : "246.680", "long" : "246.468"},
    #                             "imageURL" : "https://upload.wikimedia.org/wikipedia/commons/0/0f/Merlion_Sentosa.jpg",
    #                             "startTime" : "1800",
    #                             "endTime" : "2200"
    #                         }
    #                     }
    #                 },
    #                 "2" : {
    #                     "date" : "2024-01-02",
    #                     "activities" : {
    #                         "0" : {
    #                             "name" : "SEA Aquarium",
    #                             "location" : "Singapore",
    #                             "locationCoordinates" : {"lat" : "112.223", "long" : "223.334"},
    #                             "imageURL" : "https://image.kkday.com/v2/image/get/h_650%2Cc_fit/s1.kkday.com/product_23301/20230323024107_wG7zu/jpg",
    #                             "startTime" : "0800",
    #                             "endTime" : "1200"
    #                         },
    #                         "1" : {
    #                             "name" : "Botanical Gardens",
    #                             "location" : "Singapore",
    #                             "locationCoordinates" : {"lat" : "334.445", "long" : "445.556"},
    #                             "imageURL" : "https://www.nparks.gov.sg/-/media/nparks-real-content/gardens-parks-and-nature/sg-botanic-gardens/sbg10_047alt.ashx",
    #                             "startTime" : "1200",
    #                             "endTime" : "1600"
    #                         },
    #                         "2" : {
    #                             "name" : "Orchard Raod",
    #                             "location" : "Singapore",
    #                             "locationCoordinates" : {"lat" : "556.667", "long" : "667.778"},
    #                             "imageURL": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Presenting..._the_real_ION_%288200217734%29.jpg/1024px-Presenting..._the_real_ION_%288200217734%29.jpg",
    #                             "startTime" : "1600",
    #                             "endTime" : "2200"
    #                         }
    #                     }
    #                 },
    #                 "3" : {
    #                     "date" : "2024-01-03",
    #                     "activities" : {
    #                         "0" : {
    #                             "name" : "Gardens By The Bay",
    #                             "location" : "Singapore",
    #                             "locationCoordinates" : {"lat" : "234.432", "long" : "243.342"},
    #                             "imageURL" : "https://afar.brightspotcdn.com/dims4/default/ada5ead/2147483647/strip/true/crop/728x500+36+0/resize/660x453!/quality/90/?url=https%3A%2F%2Fafar-media-production-web.s3.us-west-2.amazonaws.com%2Fbrightspot%2F94%2F46%2F4e15fcdc545829ae3dc5a9104f0a%2Foriginal-7d0d74d7c60b72c7e76799a30334803e.jpg",
    #                             "startTime" : "1000",
    #                             "endTime" : "1800"
    #                         },
    #                         "1" : {
    #                             "name" : "Chinatown",
    #                             "location" : "Singapore",
    #                             "locationCoordinates" : {"lat" : "198.898", "long" : "278.298"},
    #                             "imageURL" : "https://www.tripsavvy.com/thmb/bikgORwUriJhkcbmyRAbEsl_thQ=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/2_chinatown_street_market-5c459281c9e77c00018d54a2.jpg",
    #                             "startTime" : "1800",
    #                             "endTime" : "2100"
    #                         }
    #                     }
    #                 }
    #             }
    #         }
    #     }
    
    if 'DebugMode' in os.environ and os.environ['DebugMode'] == 'True':
        DI.data["itineraries"] = {
            "abc123": {
                "title" : "My Itinerary",
                "description" : "3 days itinerary in Singapore",
                "generationDateTime" : datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat),
                "targetAccountID": "0d91f3f46a5645d48630a905844e9246",
                "days" : {
                    "1" : {
                        "date" : "2024-01-01",
                        "activities" : {
                            "0" : {
                                "name" : "Marina Bay Sands",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "123.456", "long" : "321.654"},
                                "imageURL" : "https://mustsharenews.com/wp-content/uploads/2023/03/MBS-Expansion-Delay-FI.jpg",
                                "startTime" : "0800",
                                "endTime" : "1000"
                            },
                            "1" : {
                                "name" : "Universal Studios Singapore",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "135.579", "long" : "579.135"},
                                "imageURL" : "https://static.honeykidsasia.com/wp-content/uploads/2021/02/universal-studios-singapore-kids-family-guide-honeykids-asia-900x643.jpg",
                                "startTime" : "1000", 
                                "endTime" : "1800"
                            },
                            "2" : {
                                "name" : "Sentosa",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "246.680", "long" : "246.468"},
                                "imageURL" : "https://upload.wikimedia.org/wikipedia/commons/0/0f/Merlion_Sentosa.jpg",
                                "startTime" : "1800",
                                "endTime" : "2200"
                            }
                        }
                    },
                    "2" : {
                        "date" : "2024-01-02",
                        "activities" : {
                            "0" : {
                                "name" : "SEA Aquarium",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "112.223", "long" : "223.334"},
                                "imageURL" : "https://image.kkday.com/v2/image/get/h_650%2Cc_fit/s1.kkday.com/product_23301/20230323024107_wG7zu/jpg",
                                "startTime" : "0800",
                                "endTime" : "1200"
                            },
                            "1" : {
                                "name" : "Botanical Gardens",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "334.445", "long" : "445.556"},
                                "imageURL" : "https://www.nparks.gov.sg/-/media/nparks-real-content/gardens-parks-and-nature/sg-botanic-gardens/sbg10_047alt.ashx",
                                "startTime" : "1200",
                                "endTime" : "1600"
                            },
                            "2" : {
                                "name" : "Orchard Raod",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "556.667", "long" : "667.778"},
                                "imageURL": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Presenting..._the_real_ION_%288200217734%29.jpg/1024px-Presenting..._the_real_ION_%288200217734%29.jpg",
                                "startTime" : "1600",
                                "endTime" : "2200"
                            }
                        }
                    },
                    "3" : {
                        "date" : "2024-01-03",
                        "activities" : {
                            "0" : {
                                "name" : "Gardens By The Bay",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "234.432", "long" : "243.342"},
                                "imageURL" : "https://afar.brightspotcdn.com/dims4/default/ada5ead/2147483647/strip/true/crop/728x500+36+0/resize/660x453!/quality/90/?url=https%3A%2F%2Fafar-media-production-web.s3.us-west-2.amazonaws.com%2Fbrightspot%2F94%2F46%2F4e15fcdc545829ae3dc5a9104f0a%2Foriginal-7d0d74d7c60b72c7e76799a30334803e.jpg",
                                "startTime" : "1000",
                                "endTime" : "1800"
                            },
                            "1" : {
                                "name" : "Chinatown",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "198.898", "long" : "278.298"},
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
                "targetAccountID": "5ca056b3f3cf487aa59db436bc8970a7",
                "days" : {
                    "1" : {
                        "date" : "2024-01-01",
                        "activities" : {
                            "0" : {
                                "name" : "Marina Bay Sands",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "123.456", "long" : "321.654"},
                                "imageURL" : "https://mustsharenews.com/wp-content/uploads/2023/03/MBS-Expansion-Delay-FI.jpg",
                                "startTime" : "0800",
                                "endTime" : "1000"
                            },
                            "1" : {
                                "name" : "Universal Studios Singapore",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "135.579", "long" : "579.135"},
                                "imageURL" : "https://static.honeykidsasia.com/wp-content/uploads/2021/02/universal-studios-singapore-kids-family-guide-honeykids-asia-900x643.jpg",
                                "startTime" : "1000", 
                                "endTime" : "1800"
                            },
                            "2" : {
                                "name" : "Sentosa",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "246.680", "long" : "246.468"},
                                "imageURL" : "https://upload.wikimedia.org/wikipedia/commons/0/0f/Merlion_Sentosa.jpg",
                                "startTime" : "1800",
                                "endTime" : "2200"
                            }
                        }
                    },
                    "2" : {
                        "date" : "2024-01-02",
                        "activities" : {
                            "0" : {
                                "name" : "SEA Aquarium",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "112.223", "long" : "223.334"},
                                "imageURL" : "https://image.kkday.com/v2/image/get/h_650%2Cc_fit/s1.kkday.com/product_23301/20230323024107_wG7zu/jpg",
                                "startTime" : "0800",
                                "endTime" : "1200"
                            },
                            "1" : {
                                "name" : "Botanical Gardens",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "334.445", "long" : "445.556"},
                                "imageURL" : "https://www.nparks.gov.sg/-/media/nparks-real-content/gardens-parks-and-nature/sg-botanic-gardens/sbg10_047alt.ashx",
                                "startTime" : "1200",
                                "endTime" : "1600"
                            },
                            "2" : {
                                "name" : "Orchard Raod",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "556.667", "long" : "667.778"},
                                "imageURL": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Presenting..._the_real_ION_%288200217734%29.jpg/1024px-Presenting..._the_real_ION_%288200217734%29.jpg",
                                "startTime" : "1600",
                                "endTime" : "2200"
                            }
                        }
                    },
                    "3" : {
                        "date" : "2024-01-03",
                        "activities" : {
                            "0" : {
                                "name" : "Gardens By The Bay",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "234.432", "long" : "243.342"},
                                "imageURL" : "https://afar.brightspotcdn.com/dims4/default/ada5ead/2147483647/strip/true/crop/728x500+36+0/resize/660x453!/quality/90/?url=https%3A%2F%2Fafar-media-production-web.s3.us-west-2.amazonaws.com%2Fbrightspot%2F94%2F46%2F4e15fcdc545829ae3dc5a9104f0a%2Foriginal-7d0d74d7c60b72c7e76799a30334803e.jpg",
                                "startTime" : "1000",
                                "endTime" : "1800"
                            },
                            "1" : {
                                "name" : "Chinatown",
                                "location" : "Singapore",
                                "locationCoordinates" : {"lar" : "198.898", "long" : "278.298"},
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
    from generation.itineraryGeneration import itineraryGenBP
    app.register_blueprint(itineraryGenBP)
    
    ## Admin routes
    from admin.report import reportBP
    app.register_blueprint(reportBP)

    from admin.contact_form import contactBP
    app.register_blueprint(contactBP)
    
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

    ## API routes
    from api import apiBP
    app.register_blueprint(apiBP)

    ## Assets service
    from assets import assetsBP
    app.register_blueprint(assetsBP)

    print()
    print("All services online; boot pre-processing and setup complete.")
    print("Booting Verdex...")

    app.run(port=8000, host='0.0.0.0', debug=True)