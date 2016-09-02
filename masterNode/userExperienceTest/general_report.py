# coding=utf-8


class GeneralReport:
    def __init__(self, test_id, system, reporter, sub_time, detail_report_list):
        self.test_id = test_id
        self.system = system
        self.reporter = reporter
        self.sub_time = sub_time
        self.detail_report_list = detail_report_list