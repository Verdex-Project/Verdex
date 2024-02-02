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

    print(locations)
    print(endTimes)
    print(dateTimeObjects)
    print(days)

    #generate routes for every activity and add to dictionary
    # print(GoogleMapsService.generateRoute("Marina Bay Sands", "Universal Studios Singapore", "transit", datetime.datetime.now()))
    routes = {}
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
                    print("Origin: {}".format(days[index][locations][locationIndex]))
                    print("Destination: {}".format(days[index][locations][str(int(locationIndex) + 1)]))
                    print(days[index][dateTimeObjects][locationIndex])
                    route = GoogleMapsService.generateRoute(days[index][locations][locationIndex],days[index][locations][str(int(locationIndex) + 1)], "transit", days[index][dateTimeObjects][locationIndex])
                    cleanedRoute = cleanRoute(route,days[index][endTimes][locationIndex])
                    cleanedRoutes[index][str(routeIndex)] = cleanedRoute
                    routeIndex += 1
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

