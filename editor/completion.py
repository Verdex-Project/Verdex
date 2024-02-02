from flask import Flask,render_template,Blueprint, request,redirect,url_for
from main import DI, Universal, GoogleMapsService
import json, os
from datetime import datetime, timedelta


completionPage = Blueprint("completionPageBP",__name__)

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
    

@completionPage.route("/completion")
def completionRoot():
    if "itineraryID" not in request.args:
        return redirect(url_for("error", error="Itinerary ID is missing."))
    else:
        return redirect(url_for("completionPageBP.completionHome", itineraryID=request.args.get("itineraryID")))

@completionPage.route("/completion/<itineraryID>", methods=['GET', 'POST'])
def completionHome(itineraryID):
    if itineraryID not in DI.data["itineraries"]:
        return redirect(url_for("error",error="Itinerary Not Found"))

    cleanedRoutes = {}

    locations = []
    #get all locations

    endTimes = []
    #get end times

    dates = []

    dateTimeObjects = []

    for day in DI.data["itineraries"][itineraryID]["days"]:
        activityDate = DI.data["itineraries"][itineraryID]["days"][day]["date"]
        dates.append(activityDate)
        #get day date
        activities = DI.data["itineraries"][itineraryID]["days"][day]["activities"]
        for i in activities:
            locations.append(activities[i]["name"])

        for j in activities:
            endTime = activities[j]["endTime"]
            endTimes.append(activities[j]["endTime"])
        #create date time object
            combinedDatetimeStr = f"{activityDate} {endTime}"
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
            cleanedRoute = cleanRoute(route, endTimes[locationIndex])
            cleanedRoutes[str(locationIndex)] = cleanedRoute
    print(cleanedRoutes)

    # print(locations)
    # print(endTimes)
    # print(dateTimeObjects)


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
        itinerary_data = DI.data, 
        dayCountList = dayCountList,
        activityCountDict = activityCountDict,
        cleanedRoutes = cleanedRoutes
        )

