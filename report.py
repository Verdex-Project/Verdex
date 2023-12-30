# Blueprint for report generation
import os
from flask import Blueprint, render_template, json, request, send_file


report_display_page = Blueprint("report", __name__)

#Main report displaying webpage
@report_display_page.route('/')
def report():
    with open('test_data.json', 'r') as file:
        data = json.load(file)
    return render_template('report.html', data=data)

#Report downloading feature
@report_display_page.route('/download_report', methods=['POST'])
def download_report():
    report_id = request.form['report_id']

    with open('reports/reportsInfo.json', 'r') as read_reportsInfo:
        loaded_json = json.load(read_reportsInfo)
    
    if report_id not in loaded_json:
        return "ID not found in database, please try again."

    report_id_variable = str(report_id)

    report_folder_path = os.getcwd()
    report_file_name = f"report_{report_id_variable}.txt"
    report_file_path = os.path.join(report_folder_path, 'reports', report_file_name)

    if not os.path.isfile(report_file_path):
        return "The report file is not found in the database."
    
    #For code reviewing and debugging purposes 
    print(f"Report ID: {report_id}")
    print(f"Report File Path: {report_file_path}")

    # Use send_file to send the corresponding report txt file back
    try:
        return send_file(report_file_path, as_attachment=True)
    except Exception as e:
        return str(e)
