#!python
#coding=utf8
import time
from DataDic import dic_job_status

class ClusterJob:
    def __init__(self, job_name, worker_type, job_cmd, job_para_list):
        self.job_id = 0
        self.job_name = job_name  # 任务名称
        self.worker_type = worker_type  # 任务名称
        self.job_cmd = job_cmd    # 任务
        self.job_para_list = job_para_list #任务参数列表
        self.job_status = 0    # 0为待执行，1为执行中，2为完成
        self.job_worker = ""   # 任务执行机
        self.create_time = ""