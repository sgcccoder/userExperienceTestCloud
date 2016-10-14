# coding=utf-8

import os
import re
import zipfile

from django.core.files.storage import default_storage
from masterNode import settings

from .image_process import ImageProcess
from .models import Report, ReportPerBrowser, ImageReport, ImageInfo
from .parser import Parser


class ReportManager:
    def __init__(self, logger):
        self.logger = logger
        self.reports = {}
        self.report_num_per_test = {}

    def process(self, zip_file, system, province, city, reporter, test_id, browser):
        report_path = ""
        # 在服务器上创建路径存储巡检人员提交的报告
        try:
            report_dir = settings.MEDIA_ROOT + test_id + os.path.sep + browser
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            report_zip = zipfile.ZipFile(zip_file)
            for filename in report_zip.namelist():
                self.logger.info('filename: ' + filename)
                data = report_zip.read(filename)
                filename = os.path.split(filename)[1]
                target_path = os.path.join(report_dir, filename)
                target_file = open(target_path, 'wb+')
                target_file.write(data)
                target_file.close()
                self.logger.info(filename + u'已上传到服务器' + target_path)

            if self.report_num_per_test.has_key(test_id):
                #不是一个用户体验测试的第一份测试报告
                self.report_num_per_test[test_id] += 1
            else:
                #是一个用户体验测试的第一份测试报告
                self.report_num_per_test[test_id] = 1
                test_report = {'system': system, 'reporter': reporter}
                detail_test_reports = []
                test_report['detail'] = detail_test_reports
                test_report['image_file_names'] = []
                self.reports[test_id] = test_report

            self.logger.info(u'这是一个用户体验测试的第' + str(self.report_num_per_test[test_id]) + u'份测试报告')
            #对上传的测试报告文件进行分析，抽取摘要信息
            test_report = self.reports[test_id]
            detail_test_reports = test_report['detail']
            detail_test_report = {'report_dir': report_dir, 'province': province, 'city': city, 'browser': browser}
            for filename in report_zip.namelist():
                data = report_zip.read(filename)
                filename = os.path.split(filename)[1]

                if filename == 'report.html':
                    self.logger.info(u'找到report.html')
                    report_path = os.path.join(report_dir, filename)
                    # 抽取通过测试的数目和未通过的数目
                    pattern = re.compile(r'"fail":\d+,"label":"All Tests","pass":\d+')
                    match = pattern.search(data)
                    line = match.group()
                    nums = re.findall(r'\d+', line)
                    fail_num = int(nums[0])
                    pass_num = int(nums[1])
                    total_num = fail_num + pass_num
                    detail_test_report['pass_num'] = pass_num
                    detail_test_report['total_num'] = total_num
                    detail_test_report['report_path']=report_path
                    self.logger.info('pass_num: ' + str(pass_num)  + ' total_num: ' + str(total_num))

                elif filename == 'output.xml':
                    self.logger.info(u'找到output.xml')
                    output_xml_path = os.path.join(report_dir, filename)
                    parser = Parser(self.logger)
                    apdex_index = parser.calculate_apdex(output_xml_path)
                    detail_test_report['apdex'] = apdex_index
                    self.logger.info('apdex: ' + str(apdex_index) )
                #如果是一个用户体验测试的第一份测试报告包含的图像文件，需要记录图像文件名称
                elif self.report_num_per_test[test_id] == 1 and filename.endswith('.png'):
                    self.logger.info(u'找到' + filename)
                    test_report['image_file_names'].append(filename)
                    #默认不存续图像显示问题
                    test_report[filename] = True

            detail_test_reports.append(detail_test_report)
            test_report['detail'] = detail_test_reports

            # 同一测试所有报告都已收集完毕
            if self.report_num_per_test[test_id] == settings.BROWSER_NUM:
                # 开始图像比对
                image_processer = ImageProcess(self.logger)
                #一个用户体验测试的第一份报告的截图做为基准，其他报告的截图和该截图进行对比
                base_detail_test_report = detail_test_reports[0]
                for image_file_name in test_report['image_file_names']:
                    for i in range(1, len(detail_test_reports)):
                        detail_test_report = detail_test_reports[i]
                        image_path = detail_test_report['report_dir'] + os.path.sep + image_file_name
                        base_image_path = base_detail_test_report['report_dir'] + os.path.sep + image_file_name
                        self.logger.info(base_image_path + ' vs ' + image_path )
                        if not image_processer.process(base_image_path, image_path):
                            test_report[image_file_name] = False
                            self.logger.info(image_file_name + ': false ')
                            break  # 如果已经存在显示问题，不用再比

            self.reports[test_id] = test_report

            # 同一测试所有报告都已收集完毕
            if self.report_num_per_test[test_id] == settings.BROWSER_NUM:
                self.logger.info(u'同一测试所有报告都已收集完毕')

                #用户体验测试相关信息存入数据库
                for detail_test_report in test_report['detail']:
                    report_path = detail_test_report['report_path']
                    report_path = report_path.replace(settings.MEDIA_ROOT, '')
                    report_url = default_storage.url(report_path)
                    report_per_browser_instance = ReportPerBrowser(test_id=test_id,
                                                                   province=detail_test_report['province'],
                                                                   city=detail_test_report['city'],
                                                                   total_num=detail_test_report['total_num'],
                                                                   pass_num=detail_test_report['pass_num'],
                                                                   apdex=detail_test_report['apdex'],
                                                                   browser=detail_test_report['browser'],
                                                                   report_url=report_url)
                    report_per_browser_instance.save()
                    for image_file_name in test_report['image_file_names']:
                        image_path = detail_test_report['report_dir'] + os.path.sep + image_file_name
                        image_path = image_path.replace(settings.MEDIA_ROOT, '')
                        image_url = default_storage.url(image_path)
                        image_info_instance = ImageInfo(test_id=test_id, browser=detail_test_report['browser'], image_name=image_file_name, image_url=image_url)
                        image_info_instance.save()

                for image_file_name in test_report['image_file_names']:
                    image_report_instance = ImageReport(test_id=test_id, image_name=image_file_name,
                                                        status=test_report[image_file_name])
                    image_report_instance.save()

                report_instance = Report(test_id=test_id, reporter=test_report['reporter'],
                                         system=test_report['system'])
                report_instance.save()
                self.logger.info(u'报告存入数据库')
                return True
        except Exception, e:
            self.logger.error(e)
            return False