from flask import Flask,render_template,Blueprint, request,redirect,url_for
from main import DI, Universal, GoogleMapsService
import json, os
from datetime import datetime, timedelta

editorPage = Blueprint("editorPageBP",__name__)

def cleanRoute(route,time):
    cleanedRoute = {}
    cleanedRoute["steps"] = []

    startTime = time
    cleanedRoute["startTime"] = startTime
    print(cleanedRoute["startTime"])

    eta = route['duration']
    cleanedRoute["eta"] = eta
    print(cleanedRoute["eta"])

    copyright = route['copyright']
    cleanedRoute["copyright"] = copyright

    for stepListDictionary in route["steps"]:
        stepsDictionary = {}
        travelMode = stepListDictionary["travel_mode"]
        if travelMode == "WALKING":
            duration = stepListDictionary["duration"]["text"]
            durationString = ''.join(filter(str.isdigit, duration))
            print(durationString)

            initialTimeStr = startTime
            initialTime = datetime.strptime(initialTimeStr, "%H%M")
            arriveTime = initialTime + timedelta(minutes=int(durationString))
            arriveTime = arriveTime.strftime("%H%M")

            startInstruction = stepListDictionary["html_instructions"]

            walkIcon = "static/Images/walkIcon.png"

            transportType = "Walk"

            walkTime = stepListDictionary["duration"]["text"]

            walkDistance = stepListDictionary["distance"]["text"]

            stepsDictionary["startInstruction"] = startInstruction
            stepsDictionary["startTime"] = initialTimeStr
            stepsDictionary["arriveTime"] = arriveTime
            stepsDictionary["icon"] = walkIcon
            stepsDictionary["transportType"] = transportType
            stepsDictionary["time"] = walkTime
            stepsDictionary["distance"] = walkDistance

            cleanedRoute["steps"].append(stepsDictionary)

            startTime = arriveTime

        elif travelMode == "TRANSIT":
            duration = stepListDictionary["duration"]["text"]
            durationString = ''.join(filter(str.isdigit, duration))
            print(durationString)

            initialTimeStr = startTime
            initialTime = datetime.strptime(initialTimeStr, "%H%M")
            arriveTime = initialTime + timedelta(minutes=int(durationString))
            arriveTime = arriveTime.strftime("%H%M")

            if stepListDictionary["transit_details"]["line"]["vehicle"]["name"] == "Bus":
                transitIcon = "static/Images/busIcon.png"
                transportType = stepListDictionary["transit_details"]["line"]["vehicle"]["name"]
            if stepListDictionary["transit_details"]["line"]["vehicle"]["name"] == "Subway":
                stepListDictionary["transit_details"]["line"]["vehicle"]["name"] = "MRT"
                transitIcon = "static/Images/subwayIcon.png"
                transportType = stepListDictionary["transit_details"]["line"]["vehicle"]["name"]
            if stepListDictionary["transit_details"]["line"]["vehicle"]["name"] == "Tram":
                stepListDictionary["transit_details"]["line"]["vehicle"]["name"] = "Tram"
                transitIcon = "static/Images/subwayIcon.png"
                transportType = stepListDictionary["transit_details"]["line"]["vehicle"]["name"]

            startInstruction = stepListDictionary["html_instructions"].replace("Subway", "MRT")

            transitTime = stepListDictionary["duration"]["text"]

            transitDistance = stepListDictionary["distance"]["text"]

            departure = stepListDictionary["transit_details"]["departure_stop"]["name"]

            arrival = stepListDictionary["transit_details"]["arrival_stop"]["name"]

            name = stepListDictionary["transit_details"]["line"]["name"]

            stepsDictionary["startInstruction"] = startInstruction
            stepsDictionary["startTime"] = initialTimeStr
            stepsDictionary["arriveTime"] = arriveTime
            stepsDictionary["icon"] = transitIcon
            stepsDictionary["transportType"] = transportType
            stepsDictionary["time"] = transitTime
            stepsDictionary["distance"] = transitDistance
            stepsDictionary["departure"] = departure
            stepsDictionary["arrival"] = arrival
            stepsDictionary["name"] = name

            cleanedRoute["steps"].append(stepsDictionary)

            startTime = arriveTime
        else:
            return "TRAVEL METHOD IS NOT WALKING / TRANSIT"

    # print(stepsDictionary)
    # print(cleanedRoute)
    return cleanedRoute
    

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

    print(locations)
    print(dateTimeObjects)

    #generate routes for every activity and add to dictionary
    # print(GoogleMapsService.generateRoute("Marina Bay Sands", "Universal Studios Singapore", "transit", datetime.datetime.now()))
    routes = {}
    for locationIndex in range(len(locations)):
        if locationIndex + 1 != len(locations):
            print("Origin: {}".format(locations[locationIndex]))
            print("Destination: {}".format(locations[locationIndex + 1]))
            print(dateTimeObjects[locationIndex])
            route = GoogleMapsService.generateRoute(locations[locationIndex], locations[locationIndex + 1], "transit", dateTimeObjects[locationIndex])
            if isinstance(route,str):
                cleanedRoute = "Route Could Not Be Determined"
            else:
                cleanedRoute = cleanRoute(route, endTimes[locationIndex])
            cleanedRoutes[str(locationIndex)] = cleanedRoute
    print(cleanedRoutes)

    # print(locations)
    # print(endTimes)
    # print(dateTimeObjects)


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
        itinerary_data = DI.data, 
        dayCountList = dayCountList,
        activityCountList = activityCountList,
        cleanedRoutes = cleanedRoutes
        )




