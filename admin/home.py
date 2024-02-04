from flask import Blueprint,Flask, render_template, request, redirect, url_for, session, Blueprint, send_file
import json, os, datetime, copy
from main import DI, Logger, Analytics, Universal, FireAuth, manageIDToken, Emailer, AddonsManager, FireConn, FireRTDB, getNameAndPosition

adminHomeBP = Blueprint("admin", __name__)

@adminHomeBP.route('/admin')
def admin():
    authCheck = manageIDToken(checkIfAdmin=True)
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]
    
    name, position = getNameAndPosition(accounts=DI.data["accounts"], targetAccountID=targetAccountID)

    analyticsInternalStatus = os.environ.get("AnalyticsEnabled") == "True"
    
    analyticsAdminStatus = AddonsManager.readConfigKey("AnalyticsEnabled")
    if analyticsAdminStatus == "Key Not Found":
        AddonsManager.setConfigKey("AnalyticsEnabled", analyticsInternalStatus)
        analyticsAdminStatus = analyticsInternalStatus
    
    analyticsFinalStatus = analyticsAdminStatus and analyticsInternalStatus

    
    emailerInternalStatus = os.environ.get("EmailingServicesEnabled") == "True"

    emailerAdminStatus = AddonsManager.readConfigKey("EmailingServicesEnabled")
    if emailerAdminStatus == "Key Not Found":
        AddonsManager.setConfigKey("EmailingServicesEnabled", emailerInternalStatus)
        emailerAdminStatus = emailerInternalStatus
    
    emailerFinalStatus = emailerInternalStatus and emailerAdminStatus
    

    logged_in = 0
    user_list = FireAuth.listUsers()

    for accountID in DI.data['accounts']:
        if 'idToken' in DI.data['accounts'][accountID]:
            logged_in += 1
    
    return render_template(
        'admin/system_health.html', 
        name=name,
        position=position, 
        analyticsFinalStatus = analyticsFinalStatus,
        analyticsInternalStatus = analyticsInternalStatus,
        emailerInternalStatus = emailerInternalStatus, 
        emailerFinalStatus = emailerFinalStatus, 
        total_user = len(user_list),
        logged_in = logged_in,
        sync_status = DI.syncStatus
    )

@adminHomeBP.route('/admin/user_management', methods=['GET'])
def user_management():
    authCheck = manageIDToken(checkIfAdmin=True)
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]
    
    name, position = getNameAndPosition(accounts=DI.data["accounts"], targetAccountID=targetAccountID)

    non_admin_users = []
    for accountID in DI.data['accounts']:
        if not ('admin' in DI.data['accounts'][accountID] and DI.data['accounts'][accountID]['admin']==True):
            non_admin_users.append(DI.data['accounts'][accountID])
    
    return render_template('admin/user_management.html', users=non_admin_users, name=name, position=position)

@adminHomeBP.route('/admin/user_profile/<string:user_id>', methods=['GET'])
def user_profile(user_id):
    authCheck = manageIDToken(checkIfAdmin=True)
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    if user_id not in DI.data['accounts']:
        return redirect(url_for('error', error='User not found'))
    
    name, position = getNameAndPosition(accounts=DI.data["accounts"], targetAccountID=targetAccountID)
    
    return render_template('admin/edit_user.html', user=DI.data['accounts'][user_id], name=name, position=position)

@adminHomeBP.route('/admin/user_profile/<string:user_id>/changeEmail', methods= ['GET'])
def changeEmail(user_id):
    new_email = request.args.get("newEmail")
    for accountID in DI.data['accounts']:
        if DI.data['accounts'][accountID]['id'] == user_id:
            response = FireAuth.changeUserEmail(fireAuthID=DI.data["accounts"][accountID]["fireAuthID"], newEmail=new_email)
            if response != True:
                Logger.log("ADMIN USERMANAGEMENT ERROR: Failed to get FireAuth to change email for account ID '{}'; response: {}".format(accountID, response))
                return redirect(url_for('error', error='Failed to change email. Please try again.'))
            
            DI.data['accounts'][accountID]['email'] = new_email
            DI.save()

            Logger.log(f'ADMIN CHANGEEMAIL: Account with ID {accountID} has changed their email to {new_email}.')
            
            return redirect(url_for('admin.user_management'))
        
    return redirect(url_for('error', error='User not found'))

@adminHomeBP.route('/admin/user_profile/<string:user_id>/delete', methods=['GET'])
def deleteAccount(user_id):
    for accountID in DI.data['accounts']:
        if DI.data['accounts'][accountID]['id'] == user_id:
            response = FireAuth.deleteAccount(DI.data['accounts'][accountID]['fireAuthID'], admin=True)
            if isinstance(response, str):
                Logger.log("ADMIN USERMANAGEMENT ERROR: Failed to get FireAuth to delete account ID '{}'; response: {}".format(accountID, response))
                return "ERROR: Failed to delete account."
            del DI.data['accounts'][accountID]
            DI.save()
            Logger.log(f'ADMIN DELETEACCOUNT: Account with ID {accountID} has been deleted')
            return redirect(url_for('admin.user_management'))
    
    return redirect(url_for('error', error='User not found'))
    
@adminHomeBP.route('/admin/user_profile/<string:user_id>/ban')
def banAccount(user_id):
    for accountID in DI.data['accounts']:
        if DI.data['accounts'][accountID]['id'] == user_id:
            DI.data['accounts'][accountID]['forumBanned'] = True
            DI.save()
            Logger.log(f'ADMIN BANACCOUNT: Account with ID {accountID} has been banned from Verdextalks')
            return redirect(url_for('admin.user_management'))

    return redirect(url_for('error', error='User not found'))

@adminHomeBP.route('/admin/user_profile/<string:user_id>/unban')
def unbanAccount(user_id):
    for accountID in DI.data['accounts']:
        if DI.data['accounts'][accountID]['id'] == user_id:
            DI.data['accounts'][accountID]['forumBanned'] = False
            DI.save()
            Logger.log(f'ADMIN BANACCOUNT: Account with ID {accountID} has been unbanned from Verdextalks')
            return redirect(url_for('admin.user_management'))
        
    return redirect(url_for('error', error='User not found'))

@adminHomeBP.route('/admin/user_profile/<string:user_id>/logout')
def logoutAccount(user_id):
    for accountID in DI.data['accounts']:
        if DI.data['accounts'][accountID]['id'] == user_id:
            if 'idToken' in DI.data['accounts'][accountID]:
                del DI.data['accounts'][accountID]['idToken']
            if 'refreshToken' in DI.data['accounts'][accountID]:
                del DI.data['accounts'][accountID]['refreshToken']
            if 'tokenExpiry' in DI.data['accounts'][accountID]:
                del DI.data['accounts'][accountID]['tokenExpiry']
            DI.save()
            
            Logger.log(f'ADMIN LOGOUTACCOUNT: Account with ID {accountID} has been logged out')
            return redirect(url_for('admin.user_management'))
        
    return redirect(url_for('error', error='User not found'))

@adminHomeBP.route('/admin/report')
def report():
    authCheck = manageIDToken(checkIfAdmin=True)
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]
    
    name, position = getNameAndPosition(accounts=DI.data["accounts"], targetAccountID=targetAccountID)
    
    with open('reports/reportsInfo.json', 'r') as file:
        data = json.load(file)
    
    for key in data:
        data[key]['timestamp'] = datetime.datetime.strptime(data[key]['timestamp'], Universal.systemWideStringDatetimeFormat).strftime("%d %b %Y %I:%M %p")
    
    return render_template('admin/report.html', data=data, name=name, position=position, permission=Analytics.checkPermissions())

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
        return redirect(url_for('error'))

    local_path = os.getcwd() #Need to change this
    report_file_name = f"report-{report_id}.txt"
    full_report_file_path = os.path.join(local_path, 'reports', report_file_name)

    if not os.path.isfile(full_report_file_path):
        Logger.log("ADMIN REPORT ERROR: Report file was not found for report ID '{}'.".format(report_id))
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
        return redirect(url_for('error'))
    try:
        os.remove(report_file_path)
        with open('reports/reportsInfo.json', 'r') as file:
            data = json.load(file)
        del data[report_id]
        with open('reports/reportsInfo.json', 'w') as file:
            json.dump(data, file)
        Logger.log("ADMIN DELETE_REPORT: Report with ID '{}' deleted.".format(report_id))
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
    # Redirect to the report page after clearing data
    return redirect(url_for('admin.report'))


@adminHomeBP.route('/admin/customer_support')
def reply():
    questions = []
    authCheck = manageIDToken(checkIfAdmin=True)
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    name, position = getNameAndPosition(accounts=DI.data["accounts"], targetAccountID=targetAccountID)
    
    if 'supportQueries' not in DI.data['admin']:
        return render_template('admin/reply.html', name=name, position=position, questions_list = questions)
    for question in DI.data['admin']['supportQueries']:
        question_id = question
        question_name = DI.data['admin']['supportQueries'][question]['name']
        email = DI.data['admin']['supportQueries'][question]['email']
        message = DI.data['admin']['supportQueries'][question]['message']
        timestamp = datetime.datetime.strptime(DI.data['admin']['supportQueries'][question]['timestamp'], Universal.systemWideStringDatetimeFormat).strftime("%d %b %Y %I:%M %p")
        support = {
            'id': question_id,
            'name': question_name,
            'email': email,
            'message': message,
            'timestamp': timestamp
        }
        questions.append(support)

    return render_template('admin/reply.html', name=name, position=position, questions_list = questions)

@adminHomeBP.route('/admin/type_reply/<string:question_id>', methods=['GET', 'POST'])
def type_reply(question_id):
    authCheck = manageIDToken(checkIfAdmin=True)
    if not authCheck.startswith("SUCCESS"):
        return redirect(url_for("unauthorised", error=authCheck[len("ERROR: ")::]))
    targetAccountID = authCheck[len("SUCCESS: ")::]

    name, position = getNameAndPosition(accounts=DI.data["accounts"], targetAccountID=targetAccountID)

    for questionID in DI.data['admin']['supportQueries']:
        if questionID == question_id:
            question = DI.data['admin']['supportQueries'][questionID]
            question_name = question['name']
            question_email = question['email']
            question_message = question['message']
            question_timestamp = datetime.datetime.strptime(question['timestamp'], Universal.systemWideStringDatetimeFormat).strftime("%d %b %Y %I:%M %p")
            return render_template('admin/type_reply.html', name=name, position=position, 
                                   question_id = question_id,
                                    question_name = question_name, 
                                    question_email = question_email, 
                                    question_message = question_message,
                                    question_timestamp = question_timestamp)

    return redirect(url_for('admin.reply'))
    