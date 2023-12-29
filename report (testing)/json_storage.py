import json

class PersistentStorage:
    def __init__(self, storage_file='reports.json'):
        self.storage_file = storage_file
        self.reports = []

        # Load existing reports from the storage file
        self.load_reports()

    def save_report(self, report_data):
        self.reports.append(report_data)
        self._save_to_storage()

    def get_reports(self):
        return self.reports

    def _save_to_storage(self):
        with open(self.storage_file, 'w') as file:
            json.dump(self.reports, file)

    def load_reports(self):
        try:
            with open(self.storage_file, 'r') as file:
                self.reports = json.load(file)
        except FileNotFoundError:
            # If the file doesn't exist yet, initialize an empty list
            self.reports = []
