from flask import Blueprint,Flask, render_template, request, redirect, url_for, flash, session, Blueprint, send_file
import json, os, datetime
from models import  *
from analytics import Analytics
adminHomeBP = Blueprint("admin", __name__)

@adminHomeBP.route('/admin/dashboard')
def home():
    return render_template('admin/home.html')
@adminHomeBP.route('/admin/user_management')
def user_management():
    return render_template('admin/user_management.html')
@adminHomeBP.route('/admin/report')
def report():
    with open('reports/reportsInfo.json', 'r') as file:
        data = json.load(file)
    return render_template('admin/report.html', data=data, date = datetime.datetime.now().strftime("%d %b $Y %I:%M %p"))
@adminHomeBP.route('/admin/report/generate', methods=['POST', 'GET'])
def generate_report():
    Analytics.generateReport()
    return redirect(url_for('admin.report'))
@adminHomeBP.route('/admin/report/<report_id>', methods=['POST', 'GET'])
def download_report(report_id):
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
@adminHomeBP.route('/admin/report/delete/<report_id>', methods=['POST', 'GET'])
def delete_report(report_id):
    report_file_path = os.path.join(Analytics.reportsFolderPath, f'report-{report_id}.txt')
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
        return redirect(url_for('admin.report'))
    except Exception as e:
        return str(e)
@adminHomeBP.route('/admin/report/delete/all', methods=['POST', 'GET'])
def delete_all_reports():
    try:
        for filename in os.listdir(Analytics.reportsFolderPath):
            if filename != "reportsInfo.json":
                os.remove(os.path.join(Analytics.reportsFolderPath, filename))
            else:
                with open(Analytics.reportsInfoFilePath, "w") as f:
                    json.dump({}, f)

        Logger.log("ADMIN DELETE_ALL_REPORTS: All reports deleted.")
        return redirect(url_for('admin.report'))
    except Exception as e:
        return str(e)
@adminHomeBP.route('/admin/report/clear', methods=['POST', 'GET'])
def clear_data():
    with open(Analytics.filePath, "w") as metrics_file:
        json.dump(Analytics.sampleMetricsObject, metrics_file)

    Analytics.load_metrics()
    Logger.log("ADMIN CLEAR_DATA: Analytics data cleared.")
    flash("Analytics data cleared successfully.")

    # Redirect to the report page after clearing data
    return redirect(url_for('admin.report'))
@adminHomeBP.route('/system_health')
def system_health():
    return render_template('admin/system_health.html')
@adminHomeBP.route('/reply')
def reply():
    return render_template('admin/reply.html')