from flask import Flask,render_template,Blueprint, request,redirect,url_for
from main import DI, Universal, GoogleMapsService, cleanRoute, manageIDToken
import json, os
from datetime import datetime, timedelta


completionPage = Blueprint("completionPageBP",__name__)

@completionPage.route("/completion")
def completionRoot():
    if "itineraryID" not in request.args:
        return redirect(url_for("error", error="Itinerary ID is missing."))
    else:
        return redirect(url_for("completionPageBP.completionHome", itineraryID=request.args.get("itineraryID")))

@completionPage.route("/completion/<itineraryID>", methods=['GET', 'POST'])
def completionHome(itineraryID):
    authCheck = manageIDToken()
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if itineraryID not in DI.data["itineraries"]:
        return redirect(url_for("error",error="Itinerary Not Found"))
    if DI.data["itineraries"][itineraryID]["associatedAccountID"] != targetAccountID:
        return redirect(url_for("error",error="You do not have permission to view this itinerary."))

    cleanedRoutes = {}

    locations = {}
    #get all locations

    endTimes = {}
    #get end times

    days = {}

    dateTimeObjects = {}

    for day in DI.data["itineraries"][itineraryID]["days"]:
        days[day] = {}
        days[day]["locations"] = {}
        days[day]["endTimes"] = {}
        days[day]["dateTimeObjects"] = {}
        locations = {}
        endTimes = {}
        dateTimeObjects = {}
        activityDate = DI.data["itineraries"][itineraryID]["days"][day]["date"]
        # dates.append(activityDate)
        #get day date
        activities = DI.data["itineraries"][itineraryID]["days"][day]["activities"]
        for i in activities:
            locations[i] = {}
            locations[i] = activities[i]["name"]
            days[day]["locations"] = locations

        for j in activities:
            endTimes[j] = {}
            endTimes[j] = activities[j]["endTime"]
        #create date time object
            endTime = DI.data["itineraries"][itineraryID]["days"][day]["activities"][j]["endTime"]
            combinedDatetimeStr = f"{activityDate} {endTime}"
            dateObject = datetime.strptime(combinedDatetimeStr, "%Y-%m-%d %H%M")
            dateTimeObjects[j] = {}
            dateTimeObjects[j] = dateObject
        days[day]["locations"] = locations
        days[day]["endTimes"] = endTimes
        days[day]["dateTimeObjects"] = dateTimeObjects

    #generate routes for every activity and add to dictionary
    for dayIndex in range(len(days)):
        routeIndex = 0
        index = str(dayIndex + 1)
        cleanedRoutes[index] = {}
        locations = "locations"
        endTimes = "endTimes"
        dateTimeObjects = "dateTimeObjects"
        if locations in days[index] and endTimes in days[index] and dateTimeObjects in days[index]:
            for locationIndex in range(len(days[index][locations])):
                if locationIndex + 1 != len(days[index][locations]):
                    locationIndex = str(locationIndex)
                    try:
                        route = GoogleMapsService.generateRoute(days[index][locations][locationIndex],days[index][locations][str(int(locationIndex) + 1)], "transit", days[index][dateTimeObjects][locationIndex])
                        if isinstance(route,str):
                            cleanedRoute = "Route Could Not Be Determined"
                        else:
                            cleanedRoute = cleanRoute(route,days[index][endTimes][locationIndex])
                    except Exception as e:
                        cleanedRoute = "Route Could Not Be Determined"
                        print("EDITOR EDITORDAY ERROR: Failed to generate route for transit from '{}' to '{}'; error: {}".format(e))
                    cleanedRoutes[index][str(routeIndex)] = cleanedRoute
                    routeIndex += 1

    dayCountList = []
    for key in DI.data["itineraries"][itineraryID]["days"]:
        dayCountList.append(str(key))

    activityCountDict = {}
    activityCounts = []
    for key1 in DI.data["itineraries"][itineraryID]["days"]:
        for key2 in DI.data["itineraries"][itineraryID]["days"][key1]["activities"]:
            activityCounts.append(str(key2))
        activityCountDict[str(key1)] = activityCounts

    return render_template(
        "editor/completion.html", 
        itineraryID=itineraryID,
        itinerary_data = DI.data["itineraries"], 
        dayCountList = dayCountList,
        activityCountDict = activityCountDict,
        cleanedRoutes = cleanedRoutes
        )

