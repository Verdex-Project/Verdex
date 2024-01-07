# Blueprint for report generation
import os
from main import Logger
from flask import Blueprint, render_template, json, request, send_file, flash, redirect, url_for

reportBP = Blueprint("report", __name__)

#Main report displaying webpage
@reportBP.route('/report')
def report():
    with open('templates/admin/test_data.json', 'r') as file:
        data = json.load(file)
    return render_template('admin/report.html', data=data)

#Report downloading feature
@reportBP.route('/report/<report_id>', methods=['POST'])
def download_report(report_id):
    report_id = request.form['report_id']

    #Checks if reportsInfo.json file exists, added this after merging
    reportsInfoPath = os.path.join(os.getcwd(), "reports", "reportsInfo.json")
    if not os.path.isfile(reportsInfoPath):
        with open(reportsInfoPath, "w") as file:
            file.write("{}")

    with open(reportsInfoPath, 'r') as read_reportsInfo:
        loaded_json = json.load(read_reportsInfo)
    
    if report_id not in loaded_json:
        flash("ERROR: Invalid report ID.")
        return redirect(url_for('error'))

    local_path = os.getcwd() #Need to change this
    report_file_name = f"report_{report_id}.txt"
    full_report_file_path = os.path.join(local_path, 'reports', report_file_name)

    if not os.path.isfile(full_report_file_path):
        Logger.log("ADMIN REPORT ERROR: Report file was not found for report ID '{}'.".format(report_id))
        flash("ERROR: Report not found.")
        return redirect(url_for('error'))
    
    Logger.log("ADMIN DOWNLOAD_REPORT: Report with ID '{}' downloaded.".format(report_id))

    # Use send_file to send the corresponding report txt file back
    try:
        return send_file(full_report_file_path, as_attachment=True)
    except Exception as e:
        return str(e)
