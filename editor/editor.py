from flask import Flask,render_template,Blueprint, request
from flask_cors import CORS
import json

editorPage = Blueprint("editorPageBP",__name__)

@editorPage.route("/editor", methods=['GET', 'POST'])
def editor():
    global itinerary_data 

    itinerary_data = itinerary_data if 'itinerary_data' in globals() else {}

    if request.method == 'GET':
        with open('templates/editor/itinerary.json', 'r+') as file:
            itinerary_data = json.load(file)

    global confirmDelete 
    confirmDelete = request.form.get('data')
    if request.method == 'POST' and confirmDelete and confirmDelete.lower() == 'true' :
        day_to_delete = request.form['deleteDay']
            # Check if the day exists in the itinerary_data
        if day_to_delete in itinerary_data:
            # Delete the day from the itinerary_data
            del itinerary_data[day_to_delete]

        with open('templates/editor/itinerary.json', 'w') as file:
            json.dump(itinerary_data, file, indent=4)

    if request.method == 'POST' and 'addDay' in request.form:
        new_day = {"activities": {"1": {"name": "Placeholder Activity"}}}
        day_number = len(itinerary_data) + 1
        while str(day_number) in itinerary_data:
            day_number += 1
        itinerary_data[str(day_number)] = new_day

        with open('templates/editor/itinerary.json', 'r+') as file:
            json.dump(itinerary_data, file, indent=4)
    
    if request.method == 'POST' and 'confirmEdit' in request.form:
        if request.form.get('new_name') is not None and request.form.get('new_name').strip() != "":
            day = request.form.get('day')
            activity_number = request.form.get('activity_number')
            new_name = request.form.get('new_name')
            itinerary_data[day]['activities'][activity_number]['name'] = new_name
        else:
            pass

        with open('templates/editor/itinerary.json', 'w') as file:
                json.dump(itinerary_data, file, indent=4)

    confirm_delete_itinerary = request.form.get('confirmDeleteItinerary')
    if request.method == 'POST' and str(confirm_delete_itinerary).lower() == 'true':
        del itinerary_data
        with open('templates/editor/itinerary.json', 'w') as file:
            json.dump(itinerary_data, file, indent=4)

    if request.method == 'POST' and 'addNewActivity' in request.form:
        if request.form.get('new_activity') is not None and request.form.get('new_activity').strip() != "":
            day = request.form.get('day')
            new_activity_name = request.form.get('new_activity')

            activity_number = str(len(itinerary_data[day]['activities']) + 1)
            itinerary_data[day]['activities'][activity_number] = {"name": new_activity_name}
        else:
            pass

        with open('templates/editor/itinerary.json', 'w') as file:
                json.dump(itinerary_data, file, indent=4)

    if request.method == 'POST' and 'deleteActivity' in request.form:
        day_to_delete = request.form['day']
        activity_number_to_delete = request.form['activity_number']

        if day_to_delete in itinerary_data and activity_number_to_delete in itinerary_data[day_to_delete]['activities']:
            del itinerary_data[day_to_delete]['activities'][activity_number_to_delete]

            with open('templates/editor/itinerary.json', 'w') as file:
                json.dump(itinerary_data, file, indent=4)

    return render_template("editor/editorNew.html", itinerary_data=itinerary_data)

    # if request.method == 'GET':
    #     day_to_delete = request.args.get("deleteDayButton")
    #     if day_to_delete in itinerary_data:
    #         del itinerary_data[day_to_delete]
    #     with open('templates/editor/itinerary.json', 'w') as file:
    #         json.dump(itinerary_data, file, indent=4)

# @editorPage.route('/editor/<day>', methods=['GET'])
# def fetchItineraryData(day):
#     day = request.form['day']
#     if day not in itinerary_data:
#         flash("ERROR: The day was not found.")
#         return redirect(url_for('error'))



