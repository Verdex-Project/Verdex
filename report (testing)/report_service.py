class ReportService:
    def __init__(self, database, persistent_storage):
        self.database = database
        self.persistent_storage = persistent_storage

    def generate_report(self):
        data = self.database.get_data()
        report = f"Report for {data}"

        # Save the report to JSON-based persistent storage
        self.persistent_storage.save_report(report)

        return report
