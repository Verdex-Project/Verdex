import os, json, uuid, random, datetime
from models import Logger, Universal
from dotenv import load_dotenv
load_dotenv()

class Analytics:
    data = []
    adminEnabled = False
    filePath = os.path.join(os.getcwd(), "analytics.json")
    reportsFolderPath = os.path.join(os.getcwd(), "reports")
    reportsInfoFilePath = os.path.join(reportsFolderPath, "reportsInfo.json")
    sampleMetricsObject = {
        "get_request": 0,
        "post_request": 0,
        "question_answered": 0,
        "sign_ins": 0,
        "sign_outs": 0,
        "forum_posts": 0,
    }

    class EventTypes:
        get_request = "get_request"
        post_request = "post_request"
        question_answered = "question_answered"
        sign_in = "sign_ins"
        sign_out = "sign_outs"
        forumPost = "forum_posts"

    @staticmethod
    def checkPermissions():
        return ("AnalyticsEnabled" in os.environ and os.environ["AnalyticsEnabled"] == "True") and Analytics.adminEnabled

    @staticmethod
    def generateRandomID(customLength=None):
        if customLength == None:
            randomID = uuid.uuid4().hex

            return randomID
        else:
            options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            randomID = ''
            for i in range(customLength):
                randomID += random.choice(options)
            return randomID

    @staticmethod
    def setup(adminEnabled: bool=True):
        Analytics.adminEnabled = adminEnabled

        if not Analytics.checkPermissions():
            print("ANALYTICS: Analytics disabled as operation permission was not granted.")
            return True
        
        try:
            ## Create analytics data file if it does not exist
            if not os.path.isfile(Analytics.filePath):
                with open(Analytics.filePath, "w") as f:
                    json.dump(Analytics.sampleMetricsObject, f)
                Analytics.data = Analytics.sampleMetricsObject
            else:
                with open(Analytics.filePath, "r") as metrics:
                    Analytics.data = json.load(metrics)

            ## Create reports folder if it does not exist
            if not os.path.isdir(Analytics.reportsFolderPath):
                os.mkdir(Analytics.reportsFolderPath)
            
            ## Create reportsInfo.json in reports folder if it does not exist
            if not os.path.isfile(Analytics.reportsInfoFilePath):
                with open(Analytics.reportsInfoFilePath, "w") as f:
                    json.dump({}, f)

            print("ANALYTICS: Analytics setup completed.")
            return True
        except Exception as e:
            Logger.log("ANALYTICS SETUP ERROR: Failed to setup environment for analytics; error: {}".format(e))
            return False

    @staticmethod
    def load_metrics():
        if not Analytics.checkPermissions():
            Logger.log("ANALYTICS LOAD_METRICS: Permission not granted to load metrics from data file.")
            return False
        
        try:
            ## Create analytics data file if it does not exist
            if not os.path.isfile(Analytics.filePath):
                with open(Analytics.filePath, "w") as f:
                    json.dump(Analytics.sampleMetricsObject, f)
                Analytics.data = Analytics.sampleMetricsObject
            else:
                with open(Analytics.filePath, "r") as metrics:
                    Analytics.data = json.load(metrics)
            
            return True
        except Exception as e:
            Logger.log(f"ANALYTICS LOAD_METRICS ERROR: Failed to load metrics from data file; error: {e}")
            return False

    @staticmethod
    def save_metrics():
        if not Analytics.checkPermissions():
            Logger.log("ANALYTICS SAVE_METRICS: Permission not granted to save metrics to data file.")
            return False
        
        try:
            with open(Analytics.filePath, "w") as f:
                json.dump(Analytics.data, f)
            
            return True
        except Exception as e:
            Logger.log("ANALYTICS SAVE_METRICS ERROR: Failed to save metrics; error: {}".format(e))
            return False
    
    @staticmethod
    def add_metrics(event_type: str):
        if not Analytics.checkPermissions():
            Logger.log("ANALYTICS ADD_METRICS: Metric update for event '{}' ignored due to insufficient permissions.".format(event_type), debugPrintExplicitDeny=True)
            return True

        if event_type not in [Analytics.EventTypes.get_request, Analytics.EventTypes.post_request, Analytics.EventTypes.question_answered, Analytics.EventTypes.sign_in, Analytics.EventTypes.sign_out, Analytics.EventTypes.forumPost]:
            return False
        
        try:
            Analytics.data[event_type] += 1
            Analytics.save_metrics()
        except Exception as e:
            Logger.log("ANALYTICS ADD_METRICS ERROR: Failed to update metrics for event type '{}'; error: {}".format(event_type, e))
            return False

        return True
    @staticmethod
    def minus_metrics(event_type: str):
        if not Analytics.checkPermissions():
            Logger.log("ANALYTICS MINUS_METRICS: Metric update for event '{}' ignored due to insufficient permissions.".format(event_type))
            return True

        if event_type not in [Analytics.EventTypes.get_request, Analytics.EventTypes.post_request, Analytics.EventTypes.question_answered, Analytics.EventTypes.sign_in, Analytics.EventTypes.sign_out, Analytics.EventTypes.forumPost]:
            return False
        
        try:
            Analytics.data[event_type] -= 1
            Analytics.save_metrics()
        except Exception as e:
            Logger.log("ANALYTICS MINUS_METRICS ERROR: Failed to update metrics for event type '{}'; error: {}".format(event_type, e))
            return False

        return True
    @staticmethod
    def generateReport():
        ## Check for permission
        if not Analytics.checkPermissions():
            print("ANALYTICS GENERATEREPORT: Generate report attempt ignored due to insufficient permissions.")
            Logger.log("ANALYTICS GENERATEREPORT: Generate report attempt ignored due to insufficient permissions.", debugPrintExplicitDeny=True)
            return "ERROR: Insufficient permissions to generate report."
        
        ## Check whether reports folder exists; if not, create using os.mkdir
        
        ## Check whether analytics data has been loaded (Analytics.data != {})
        if Analytics.data == []:
            print("ANALYTICS GENERATEREPORT: Analytics data not loaded; Loading now.")
            Logger.log("ANALYTICS GENERATEREPORT: Analytics data not loaded; Loading now.")
            Analytics.load_metrics()
        
        ## Fill in metrics data into a massive string
        report_text = f"""VERDEX ANALYTICS REPORT
-----------------------
This report was generated on {datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)} 
-----------------------
In this report a few metrics are shown. These matrices are:
- Number of requests made to the Verdex Server
- Number of questions answered from contact us form
- Number of sign ins to the Verdex Server
- Number of sign outs from the Verdex Server
- Number of Verdex Talks posts
-----------------------
The metrics are shown below:
- Number of Get Requests: {Analytics.data[Analytics.EventTypes.get_request]}
- Number of Post Requests: {Analytics.data[Analytics.EventTypes.post_request]}
- Number of Total Requests: {Analytics.data[Analytics.EventTypes.get_request] + Analytics.data[Analytics.EventTypes.post_request]}
- Number of Questions Answered: {Analytics.data[Analytics.EventTypes.question_answered]}
- Number of Sign Ins: {Analytics.data[Analytics.EventTypes.sign_in]}
- Number of Sign Outs: {Analytics.data[Analytics.EventTypes.sign_out]}
- Number of Verdex Talks Posts: {Analytics.data[Analytics.EventTypes.forumPost]}
-----------------------
"""
        ## Use open(os.path.join(os.getcwd(), "reports", "report-<UNIQUE STRING 4 CHARS LONG>.txt"), "w") to dump the massive report string into the report file
        # Generate a different ID for reportsInfo.json creation

        unique_string = datetime.datetime.now().strftime("%Y%m%dT%H%M%S") + Analytics.generateRandomID(customLength=4)
        report_timestamp = datetime.datetime.now().strftime(Universal.systemWideStringDatetimeFormat)
        report_path = os.path.join(Analytics.reportsFolderPath, f"report-{unique_string}.txt")
        with open(report_path, "w") as report:
            report.write(report_text)
        
        ## Check if reportsInfo.json exists; if not, create it
        if not os.path.isfile(Analytics.reportsInfoFilePath):
            with open(Analytics.reportsInfoFilePath, "w") as reports_info_file:
                json.dump({}, reports_info_file)
        
        # Update reportsInfo.json
        with open(Analytics.reportsInfoFilePath, "r") as f:
            reportsInfo = json.load(f)

        reportsInfo[unique_string] = {
            "report_id": unique_string,
            "timestamp": report_timestamp,
            "get_request": Analytics.data[Analytics.EventTypes.get_request],
            "post_request": Analytics.data[Analytics.EventTypes.post_request],
            "total_requests": Analytics.data[Analytics.EventTypes.get_request] + Analytics.data[Analytics.EventTypes.post_request],
            "question_answered": Analytics.data[Analytics.EventTypes.question_answered],
            "sign_ins": Analytics.data[Analytics.EventTypes.sign_in],
            "sign_outs": Analytics.data[Analytics.EventTypes.sign_out],
            "verdex_talks_posts": Analytics.data[Analytics.EventTypes.forumPost],
        }

        with open(Analytics.reportsInfoFilePath, "w") as f:
            json.dump(reportsInfo, f)
        
        ## Return success message
        return report_timestamp