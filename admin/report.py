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
    report_file_name = f"report-{report_id}.txt"
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
            if filename != "reportsInfo.json":
                os.remove(os.path.join(Analytics.reportsFolderPath, filename))
            else:
                with open(Analytics.reportsInfoFilePath, "w") as f:
                    json.dump({}, f)

        Logger.log("ADMIN DELETE_ALL_REPORTS: All reports deleted.")
        return redirect(url_for('report.report'))
    except Exception as e:
        return str(e)

@reportBP.route('/report/clear', methods=['POST', 'GET'])
def clear_data():
    with open(Analytics.filePath, "w") as metrics:
        Analytics.data = json.dump(Analytics.sampleMetricsObject, metrics)
    Logger.log("ADMIN CLEAR_DATA: Analytics data cleared.")
    flash("Analytics data cleared successfully.")
    return redirect(url_for('report.report'))
