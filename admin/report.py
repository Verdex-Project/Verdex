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

    with open('reports/reportsInfo.json', 'r') as read_reportsInfo:
        loaded_json = json.load(read_reportsInfo)
    
    if report_id not in loaded_json:
        flash("ERROR: The report ID is not found.")
        return redirect(url_for('error'))

    report_id_variable = str(report_id)

    report_folder_path = os.getcwd() #Need to change this
    report_file_name = f"report_{report_id_variable}.txt"
    report_file_path = os.path.join(report_folder_path, 'reports', report_file_name)

    if not os.path.isfile(report_file_path):
        flash("ERROR: The report file path is not found.")
        return redirect(url_for('error'))
    
    Logger.log("ADMIN DOWNLOAD_REPORT: Report with ID '{}' downloaded.".format(report_id))

    # Use send_file to send the corresponding report txt file back
    try:
        return send_file(report_file_path, as_attachment=True)
    except Exception as e:
        return str(e)
