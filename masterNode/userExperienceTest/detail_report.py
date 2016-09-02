# coding=utf-8


class DetailReport:
    def __init__(self, browser, province, city, total_num, pass_num, apdex, report_url):
        self.browser = browser
        self.province = province
        self.city = city
        self.total_num = total_num
        self.pass_num = pass_num
        self.apdex = round(apdex, 3)
        self.report_url = report_url