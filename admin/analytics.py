import os, json, uuid, random, datetime
from models import Logger
from dotenv import load_dotenv
load_dotenv()
    
class Analytics:
    data = {}
    filePath = os.path.join(os.getcwd(), "analytics.json")

    sampleMetricsObject = {
        "get_request": 0,
        "post_request": 0,
        "question_answered": 0,
        "sign_ins": 0,
        "sign_outs": 0,
        "verdex_talks_posts": 0,
    }

    @staticmethod
    def checkPermissions():
        return "AnalyticsEnabled" in os.environ and os.environ["AnalyticsEnabled"] == "True"
    
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
    def setup():
        if not Analytics.checkPermissions():
            print("ANALYTICS: Analytics disabled as operation permission was not granted.")

        try:
            with open(Analytics.filePath, "r") as metrics:
                Analytics.data = json.load(metrics)
            print("ANALYTICS: Environment setup for analytics.")
        except FileNotFoundError:
            with open(Analytics.filePath, "w") as f:
                json.dump(Analytics.sampleMetricsObject, f)
    
    @staticmethod
    def load_metrics():
        if not Analytics.checkPermissions():
            Logger.log("ANALYTICS LOAD_METRICS: Permission not granted to load metrics from data file.")
            return False
        try:
            with open(Analytics.filePath, 'r') as metrics_file:
                Analytics.data = json.load(metrics_file)
                return True
        except Exception as e:
            Logger.log("ANALYTICS LOAD_METRICS ERROR: Failed to load metrics from data file; error: {}".format(e))
            return False
    
    @staticmethod
    def save_metrics():
        if not Analytics.checkPermissions():
            Logger.log("ANALYTICS SAVE_METRICS: Permission not granted to save metrics to data file.")
        try:
            with open(Analytics.filePath, "w") as f:
                json.dump(Analytics.data, f)
            return True
        except Exception as e:
            Logger.log("ANALYTICS SAVE_METRICS ERROR: Failed to save metrics; error: {}".format(e))
    
    @staticmethod
    def add_metrics(event_type: str):
        if not Analytics.checkPermissions():
            Logger.log("ANALYTICS ADD_METRICS: Metric update for event '{}' ignored due to insufficient permissions.".format(event_type))
            return True

        if event_type.lower() not in ["get_request", "post_request", 'question_answered', 'sign_ins', 'sign_outs', 'verdex_talks_posts']:
            return False
        
        try:
            Analytics.data[event_type.lower()] += 1
            Analytics.save_metrics()
        except Exception as e:
            Logger.log("ANALYTICS ADD_METRICS ERROR: Failed to update metrics for event type '{}'; error: {}".format(event_type.lower(), e))
            return False

        return True

    @staticmethod
    def generateReport():
        ## Check for permission
        if not Analytics.checkPermissions():
            print("ANALYTICS GENERATEREPORT: Generate report attempt ignored due to insufficient permissions.")
            Logger.log("ANALYTICS GENERATEREPORT: Generate report attempt ignored due to insufficient permissions.")
            return "ERROR: Insufficient permissions to generate report."
        ## Check whether reports folder exists; if not, create using os.mkdir
        path = 'reports'
        if not os.path.exists(path):
            os.mkdir(path)
        ## Check whether analytics data has been loaded (Analytics.data != {})
        if Analytics.data !={}:
            return True
        ## Generate your metrics
        else:
            print("ANALYTICS GENERATEREPORT: Analytics data not loaded; Loading now.")
            Logger.log("ANALYTICS GENERATEREPORT: Analytics data not loaded; Loading now.")
            Analytics.load_metrics()

        ## Fill in metrics data into a massive string
        report_text = f"""VERDEX ANALYTICS REPORT
-----------------------
This report was generated on {datetime.datetime.now().strftime("%d/%m/%Y")} at {datetime.datetime.now().strftime("%H:%M:%S")}.
-----------------------
In this report a few matrices are shown. These matrices are:
- Number of requests made to the Verdex Server
- Number of questions answered from contact us form
- Number of sign ins to the Verdex Server
- Number of sign outs from the Verdex Server
- Number of Verdex Talks posts
-----------------------
The matrices are shown below:
- Number of Get Requests: {Analytics.data['get_request']}
- Number of Post Requests: {Analytics.data['post_request']}
- Number of Total Requests: {Analytics.data['get_request'] + Analytics.data['post_request']}
- Number of Questions Answered: {Analytics.data['question_answered']}
- Number of Sign Ins: {Analytics.data['sign_ins']}
- Number of Sign Outs: {Analytics.data['sign_outs']}
- Number of Verdex Talks Posts: {Analytics.data['verdex_talks_posts']}
-----------------------
"""
        ## Use open(os.path.join(os.getcwd(), "reports", "report-<UNIQUE STRING 4 CHARS LONG>.txt"), "w") to dump the massive report string into the report file
        unique_string = Analytics.generateRandomID(4)
        with open(os.path.join(os.getcwd(), "reports", f"report-{unique_string}.txt"), "w") as report:
            report.write(report_text)
        ## Check if reportsInfo.json exists; if not, create it
        reports_info_path = os.path.join(os.getcwd(), "reports", "reportsInfo.json")
        if not os.path.exists(reports_info_path):
            # Generate a different ID for reportsInfo.json creation
            with open(reports_info_path, "w") as reports_info_file:
                json.dump({
                    unique_string: {
                        "get_request": 0,
                        "post_request": 0,
                        "total_requests": 0,
                        "question_answered": 0,
                        "sign_ins": 0,
                        "sign_outs": 0,
                        "verdex_talks_posts": 0,
                    }
                }, reports_info_file, indent=0)
        else:
            ## Update reportsInfo.json
            with open(reports_info_path, "r") as reports_info_file:
                reports_info_data = json.load(reports_info_file)
            reports_info_data[unique_string] = {
                "get_request": Analytics.data['get_request'],
                "post_request": Analytics.data['post_request'],
                "total_requests": Analytics.data['get_request'] + Analytics.data['post_request'],
                "question_answered": Analytics.data['question_answered'],
                "sign_ins": Analytics.data['sign_ins'],
                "sign_outs": Analytics.data['sign_outs'],
                "verdex_talks_posts": Analytics.data['verdex_talks_posts'],
            }

            with open(reports_info_path, "w") as reports_info_file:
                json.dump(reports_info_data, reports_info_file, indent=0)
        ## Return success message
        return 'Successfully generated report.'