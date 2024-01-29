from flask import Flask,render_template,Blueprint, request,redirect,url_for
from main import DI, Universal, GoogleMapsService
import json, os, datetime
import datetime

editorPage = Blueprint("editorPageBP",__name__)

def getETA(route):
    return route['duration']

def getArriveTime(route,index,time):
    duration = route[index]
    arriveTime = int(time) + int(duration)
    return

def cleanRoute(route, index):
    cleanedRoute = {}

    eta = route['duration']
    cleanRoute[index]["eta"] = eta

    if route["steps"]["travel_mode"] == "WALKING":
        duration = route[""]
    if route["steps"]["travel_mode"] == "TRANSIT":
        pass
    else:
        return "TRAVEL METHOD IS NOT WALKING / TRANSIT"


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

    cleanedRoute = {}

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
        dateObject = datetime.datetime.strptime(combinedDatetimeStr, "%Y-%m-%d %H%M")
        dateTimeObjects.append(dateObject)

    #generate routes for every activity and add to dictionary
    # print(GoogleMapsService.generateRoute("Marina Bay Sands", "Universal Studios Singapore", "transit", datetime.datetime.now()))
    routes = {}
    for locationIndex in range(len(locations)):
        if locationIndex + 1 != len(locations):
            print("Origin: {}".format(locations[locationIndex]))
            print("Destination: {}".format(locations[locationIndex + 1]))
            print(dateTimeObjects[locationIndex])
            route = GoogleMapsService.generateRoute(locations[locationIndex], locations[locationIndex + 1], "transit", dateTimeObjects[locationIndex])
            eta = getETA(route)
            routes[locationIndex] = route
            cleanedRoute[locationIndex] = {}
            cleanedRoute[locationIndex]["eta"] = eta
    print(routes)
    print(cleanedRoute)

    # print(locations)
    # print(endTimes)
    # print(dateTimeObjects)

    etaList = []

    for i in routes:
        etaList.append(routes[i]['duration'])
    print(etaList)

    dayCountList = []
    for key in DI.data["itineraries"][itineraryID]["days"]:
        dayCountList.append(str(key))

    activityCountList = []
    for key2 in DI.data["itineraries"][itineraryID]["days"][day]["activities"]:
        activityCountList.append(str(key2))

    # global itinerary_data 

    # itinerary_data = itinerary_data if 'itinerary_data' in globals() else {}

    # if request.method == 'GET':
    #     with open('templates/editor/itinerary.json', 'r+') as file:
    #         itinerary_data = json.load(file)

    # global confirmDelete 
    # confirmDelete = request.form.get('data')
    # if request.method == 'POST' and confirmDelete and confirmDelete.lower() == 'true' :
    #     day_to_delete = request.form['deleteDay']
    #         # Check if the day exists in the itinerary_data
    #     if day_to_delete in itinerary_data:
    #         # Delete the day from the itinerary_data
    #         del itinerary_data[day_to_delete]
    #         # Convert keys to integers, sort them, and convert back to strings

    #     with open('templates/editor/itinerary.json', 'w') as file:
    #         json.dump(itinerary_data, file, indent=4)

    # if request.method == 'POST' and 'addDay' in request.form:
    #     new_day = {"activities": {"1": {"name": "Placeholder Activity"}}}
    #     day_number = len(itinerary_data) + 1
    #     while str(day_number) in itinerary_data:
    #         day_number += 1
    #     itinerary_data[str(day_number)] = new_day

    #     with open('templates/editor/itinerary.json', 'r+') as file:
    #         json.dump(itinerary_data, file, indent=4)   
    
    # if request.method == 'POST' and 'confirmEdit' in request.form:
    #     if request.form.get('new_name') is not None and request.form.get('new_name').strip() != "":
    #         day = request.form.get('day')
    #         activity_number = request.form.get('activity_number')
    #         new_name = request.form.get('new_name')
    #         itinerary_data[day]['activities'][activity_number]['name'] = new_name
    #     else:
    #         pass

    #     with open('templates/editor/itinerary.json', 'w') as file:
    #             json.dump(itinerary_data, file, indent=4)

    # confirm_delete_itinerary = request.form.get('confirmDeleteItinerary')
    # if request.method == 'POST' and str(confirm_delete_itinerary).lower() == 'true':
    #     del itinerary_data
    #     with open('templates/editor/itinerary.json', 'w') as file:
    #         json.dump(itinerary_data, file, indent=4)

    # if request.method == 'POST' and 'addNewActivity' in request.form:
    #     if request.form.get('new_activity') is not None and request.form.get('new_activity').strip() != "":
    #         day = request.form.get('day')
    #         new_activity_name = request.form.get('new_activity')

    #         activity_number = str(len(itinerary_data[day]['activities']) + 1)
    #         itinerary_data[day]['activities'][activity_number] = {"name": new_activity_name}
    #     else:
    #         pass

    #     with open('templates/editor/itinerary.json', 'w') as file:
    #             json.dump(itinerary_data, file, indent=4)

    # if request.method == 'POST' and 'deleteActivity' in request.form:
    #     day_to_delete = request.form['day']
    #     activity_number_to_delete = request.form['activity_number']

    #     if day_to_delete in itinerary_data and activity_number_to_delete in itinerary_data[day_to_delete]['activities']:
    #         del itinerary_data[day_to_delete]['activities'][activity_number_to_delete]

    #         with open('templates/editor/itinerary.json', 'w') as file:
    #             json.dump(itinerary_data, file, indent=4)

    return render_template(
        "editor/editor.html", 
        itineraryID = itineraryID, 
        day = day, 
        itinerary_data = DI.data, 
        dayCountList = dayCountList,
        activityCountList = activityCountList
        )




