from flask import Flask,render_template,Blueprint, request,redirect,url_for
from main import DI, Universal, GoogleMapsService, cleanRoute
import json, os
from datetime import datetime, timedelta

editorPage = Blueprint("editorPageBP",__name__)

@editorPage.route("/editor")
def editorRoot():
    if "itineraryID" not in request.args:
        return redirect(url_for("error", error="Please provide the ID of the itinerary you want to edit."))
    else:
        return redirect(url_for("editorPageBP.editorHome", itineraryID=request.args.get("itineraryID")))

@editorPage.route("/editor/<itineraryID>")
def editorHome(itineraryID):
    if itineraryID not in DI.data["itineraries"]:
        return redirect(url_for("error",error="Itinerary Not Found"))

    return redirect(url_for("editorPageBP.editorDay", itineraryID=itineraryID, day=1))

@editorPage.route("/editor/<itineraryID>/<day>", methods=['GET', 'POST'])
def editorDay(itineraryID, day):

    if itineraryID not in DI.data["itineraries"]:
        return redirect(url_for("error",error="Itinerary Not Found!"))

    if day not in DI.data["itineraries"][itineraryID]["days"]:
        return redirect(url_for("error",error="Day Not Found!"))

    cleanedRoutes = {}

    locations = []
    #get all locations
    endTimes = []
    #get end times
    activityDate = DI.data["itineraries"][itineraryID]["days"][day]["date"]
    #get day date
    activities = DI.data["itineraries"][itineraryID]["days"][day]["activities"]
    for i in activities:
        locations.append(activities[i]["name"])

    for j in activities:
        endTimes.append(activities[j]["endTime"])

    #create date time object
    dateTimeObjects = []
    for time in endTimes:
        combinedDatetimeStr = f"{activityDate} {time}"
        dateObject = datetime.strptime(combinedDatetimeStr, "%Y-%m-%d %H%M")
        dateTimeObjects.append(dateObject)

    #generate routes for every activity and add to dictionary
    for locationIndex in range(len(locations)):
        if locationIndex + 1 != len(locations):
            route = GoogleMapsService.generateRoute(locations[locationIndex], locations[locationIndex + 1], "transit", dateTimeObjects[locationIndex])
            if isinstance(route,str):
                cleanedRoute = "Route Could Not Be Determined"
            else:
                cleanedRoute = cleanRoute(route, endTimes[locationIndex])
            cleanedRoutes[str(locationIndex)] = cleanedRoute
    print(cleanedRoutes)

    dayCountList = []
    for key in DI.data["itineraries"][itineraryID]["days"]:
        dayCountList.append(str(key))

    activityCountList = []
    for key2 in DI.data["itineraries"][itineraryID]["days"][day]["activities"]:
        activityCountList.append(str(key2))

    return render_template(
        "editor/editor.html", 
        itineraryID = itineraryID, 
        day = day, 
        itinerary_data = DI.data["itineraries"], 
        dayCountList = dayCountList,
        activityCountList = activityCountList,
        cleanedRoutes = cleanedRoutes,
        dayLength = len(DI.data['itineraries'][itineraryID]['days'])
        )




