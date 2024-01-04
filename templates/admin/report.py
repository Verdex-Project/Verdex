# Blueprint for report generation
import os
from flask import Blueprint, render_template, json, request, send_file, flash, redirect, url_for


reportBP = Blueprint("report", __name__)

#Main report displaying webpage
@reportBP.route('/')
def report():
    with open('templates/admin/test_data.json', 'r') as file:
        data = json.load(file)
    return render_template('admin/report.html', data=data)

#Report downloading feature
@reportBP.route('/report/<report_id>', methods=['POST'])
def download_report(report_id):
    report_id = request.form['report_id']

    #Checks if reportsInfo.json file exists, added this after merging
    if not os.path.isfile(os.path.join(os.getcwd(), "reports/reportsInfo.json")):
        with open("reports/reportsInfo.json", "w") as file:
            file.write("{}")
        #Console logging for debugging purposes
        print("-----CONSOLE LOGGING-----")
        print(f"File path that was not found: {os.path.join(str(os.getcwd()), 'reports/reportsInfo.json')}")
        print("File created and written with empty JSON object")
        print("-------END OF LOG--------")


    with open('reports/reportsInfo.json', 'r') as read_reportsInfo:
        loaded_json = json.load(read_reportsInfo)
    
    if report_id not in loaded_json:
        print("-----CONSOLE LOGGING-----")
        print(f"Report ID: {report_id} (NOT FOUND)")
        print(f"Report File Path: NONE")
        print("Download status: FAILED")
        print("ERROR: Report ID not found.")
        print("-------END OF LOG--------")
        flash("ERROR: The report ID was not found.")
        return redirect(url_for('error'))

    report_id_variable = str(report_id)

    local_path = os.getcwd() #Need to change this
    report_file_name = f"report_{report_id_variable}.txt"
    full_report_file_path = os.path.join(local_path, 'reports', report_file_name)

    if not os.path.isfile(full_report_file_path):
        print("-----CONSOLE LOGGING-----")
        print(f"Report ID: {report_id} (FOUND)")
        print(f"Report File Path: {full_report_file_path} (NOT FOUND)")
        print("Download status: FAILED")
        print("ERROR: File path not found.")
        print("-------END OF LOG--------")
        flash("ERROR: The report file path was not found.")
        return redirect(url_for('error'))
    
    #For code reviewing and debugging purposes 
    print("-----CONSOLE LOGGING-----")
    print(f"Report ID: {report_id} (FOUND)")
    print(f"Report File Path: {full_report_file_path} (FOUND)")
    print("Download status: SUCCESS")
    print("-------END OF LOG--------")

    # Use send_file to send the corresponding report txt file back
    try:
        return send_file(full_report_file_path, as_attachment=True)
    except Exception as e:
        return str(e)
