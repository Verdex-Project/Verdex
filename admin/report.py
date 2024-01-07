# Blueprint for report generation
import os
from main import Logger
from flask import Blueprint, render_template, json, request, send_file, flash, redirect, url_for
from admin.analytics import Analytics
reportBP = Blueprint("report", __name__)

#Main report displaying webpage
@reportBP.route('/report')
def report():
    with open('reports/reportsInfo.json', 'r') as file:
        data = json.load(file)
    return render_template('admin/report.html', data=data)

#Report downloading feature
@reportBP.route('/report/<report_id>', methods=['POST', 'GET'])
def download_report(report_id):
    report_id = request.form['report_id']
    with open('reports/reportsInfo.json', 'r') as read_reportsInfo:
        loaded_json = json.load(read_reportsInfo)
    
    if report_id not in loaded_json:
        flash("ERROR: The report ID is not found.")
        return redirect(url_for('error'))
    report_id_variable = str(report_id)
    report_name = f'report-{report_id_variable}.txt'
    report_folder = 'reports'
    report_file_path = os.path.join(report_folder, report_name)
    if not os.path.isfile(report_file_path):
        flash("ERROR: The report file path is not found.")
        return redirect(url_for('error'))  
    Logger.log("ADMIN DOWNLOAD_REPORT: Report with ID '{}' downloaded.".format(report_id))
    # Use send_file to send the corresponding report txt file back
    try:
        return send_file(report_file_path, as_attachment=True)
    except Exception as e:
        return str(e)
@reportBP.route('/report/delete/<report_id>', methods=['POST', 'GET'])
def delete_report(report_id):
    report_file_path = os.path.join(Analytics.reportsFolderPath, f'report-{report_id}.txt')
    Logger.log(report_file_path)
    if not os.path.isfile(report_file_path):
        flash("ERROR: The report file path is not found.")
        return redirect(url_for('error'))
    try:
        os.remove(report_file_path)
        with open('reports/reportsInfo.json', 'r') as file:
            data = json.load(file)
        del data[report_id]
        with open('reports/reportsInfo.json', 'w') as file:
            json.dump(data, file)
        Logger.log("ADMIN DELETE_REPORT: Report with ID '{}' deleted.".format(report_id))
        flash("Report deleted successfully.")
        return redirect(url_for('report.report'))
    except Exception as e:
        return str(e)
@reportBP.route('/report/delete/all', methods=['POST', 'GET'])
def delete_all_reports():
    try:
        for filename in os.listdir(Analytics.reportsFolderPath):
            if os.path.isfile(os.path.join(Analytics.reportsFolderPath, filename)):
                os.remove(os.path.join(Analytics.reportsFolderPath, filename))
        os.rmdir(Analytics.reportsFolderPath)
        Logger.log("ADMIN DELETE_ALL_REPORTS: All reports deleted.")
        flash("All reports deleted successfully.")
        Analytics.setup()
        return redirect(url_for('homepage'))
    except Exception as e:
        return str(e)
@reportBP.route('/report/clear', methods=['POST', 'GET'])
def clear_data():
    with open(Analytics.filePath, "w") as metrics:
        Analytics.data = json.dump(Analytics.sampleMetricsObject, metrics)
    Logger.log("ADMIN CLEAR_DATA: Analytics data cleared.")
    flash("Analytics data cleared successfully.")
    return redirect(url_for('report'))