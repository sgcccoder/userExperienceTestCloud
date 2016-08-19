#!python
#coding=utf8
from SimpleXMLRPCServer import SimpleXMLRPCServer
import ConfigParser
import xmlrpclib
import string
import thread
import time
import Queue
from ClusterJob import ClusterJob
from DataDic import dic_slave_status
import pdb

class Master:
    # 构造函数
    def __init__(self, ip, port, job_queue_size, heart_beat_interval):
        self.port = port
        self.ip = ip
        self.status = 0
        self.server = SimpleXMLRPCServer((ip, self.port))
        self.server.register_multicall_functions()
        self.server.register_function(self.register, 'register')
        self.server.register_function(self.heart_beat, 'heart_beat')
        self.server.register_function(self.update_status, 'update_status')
        self.server.register_function(self.get_file, 'get_file')
        self.server.register_function(self.add_job_by_para, 'add_job_by_para')
        self.server.register_function(self.get_slave_list, 'get_slave_list')
        self.server.register_function(self.add_schedule, 'add_schedule')
        self.heart_beat_interval = heart_beat_interval
        self.slave_list = {}
        self.to_do_job_queue = Queue.Queue(job_queue_size)
        self.doing_job_list = []
        self.schedule_list = []
    
    # 心跳报文
    def heart_beat(self, ip, status):
        #print "hello world"
        print "HeartBeat: " + str(ip) + " is " + dic_slave_status[status]
        self.slave_list[ip]["status"] = status        
        self.slave_list[ip]["last_live_time"] = time.time()
        return 0
    
    # 更新slave状态
    def update_status(self, ip, status):
        print "update status: " + str(ip) + " is " + dic_slave_status[status]
        self.slave_list[ip]["status"] = status
        self.slave_list[ip]["last_live_time"] = time.time()
        return 0
    
    # 注册新slave节点
    def register(self, ip, port, status, worker_type):
        url = "http://%s:%i/" % (ip, port)
        proxy = xmlrpclib.ServerProxy(url)
        self.slave_list[ip] = {"proxy":proxy, "status":status, "worker_type":worker_type, "last_live_time": time.time()}
        return (len(self.slave_list), self.heart_beat_interval)
    
    # 启动master服务
    def run(self):
        print "Master is running, listening port %d..." % self.port
        thread.start_new_thread(self.check_job_list, ())
        thread.start_new_thread(self.check_schedule, ())
        self.server.serve_forever()
    
    # 停止master服务
    def stop(self):
        self.server.server_close()
        self.status = 99
        return 0
    
    def add_job(self, job):
        if not self.to_do_job_queue.full():
            # to-do: 写入数据库，持久存储
            create_time = time.time()
            job.create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(create_time))
            job.job_id = int(create_time)
            self.to_do_job_queue.put(job)
            return job.job_id
        else:
            return -1
            
    def add_job_by_para(self, job_name, worker_type, job_cmd, job_para_list):
        job = ClusterJob(job_name, worker_type, job_cmd, job_para_list)
        return self.add_job(job)

    def get_slave_list(self):
        slaves = []
        for ip in self.slave_list.keys():
            slaves.append({"IP": ip, "status": dic_slave_status[self.slave_list[ip]["status"]]})
        return slaves
        
    def get_file(self, file_path):
        print file_path
        handle = open(file_path, "rb")
        return xmlrpclib.Binary(handle.read())
        handle.close()
    
    # 检查任务队列
    # todo：如队列不空，取出任务执行
    def check_job_list(self): 
        print "check_job_list is called: " + str(self.status)
        while self.status != 99:
            if not self.to_do_job_queue.empty():    # 如果待执行队列不为空
                print "queue is not empty"
                
                # 从队列中取出一个作业
                job = self.to_do_job_queue.get()
                
                # 找到一个空闲且worker_type匹配的slave
                idle_slave = None
                while idle_slave is None:
                    for ip in self.slave_list.keys():
                        if self.slave_list[ip]["status"] == 0 and self.slave_list[ip]["worker_type"] == job.worker_type and (time.time() - self.slave_list[ip]["last_live_time"]) < 3 * self.heart_beat_interval :
                            idle_slave = self.slave_list[ip]["proxy"]
                            break
                    else:
                        print "waiting for a " + job.worker_type + " worker..."
                        time.sleep(5)
                
                #开始执行任务
                status = idle_slave.work(job.job_id, job.job_cmd, job.job_para_list)
                if status != -1:
                    print "working"
                    # to-do: 更新数据库
                    job.job_status = 1
                    self.doing_job_list.append(job)
                    print "job_" + str(job.job_id) + "is running"
            else:           # 如果任务队列为空
                print "queue is empty"
                time.sleep(15)
    
    def check_schedule(self):
        while self.status != 99:
            #pdb.set_trace()
            for scheduled_task in self.schedule_list:
                current_time = time.localtime()
                if self.match_time(scheduled_task["time"], current_time) and not self.is_same_minute(scheduled_task["last_run_time"], current_time):
                    # 找到符合时间的任务
                    print "run a scheduled task: " + time.strftime("%Y-%m-%d %H:%M:%S", current_time)
                    
                    # 取出定时任务
                    job = scheduled_task["job"]
                    
                    idle_slave = None
                    while idle_slave is None:
                        for ip in self.slave_list.keys():
                            if self.slave_list[ip]["status"] == 0 and self.slave_list[ip]["worker_type"] == job.worker_type and (time.time() - self.slave_list[ip]["last_live_time"]) < 3 * self.heart_beat_interval :
                                idle_slave = self.slave_list[ip]["proxy"]
                                break
                        else:
                            time.sleep(5)
                    print "working"
                    
                    status = idle_slave.work(job.job_id, job.job_cmd, job.job_para_list)
                    scheduled_task["last_run_time"] = time.localtime()
                    if status != -1:
                        # to-do: 更新数据库
                        job.job_status = 1
                        self.doing_job_list.append(job)
                        print "job_" + str(job.job_id) + "is running" 
    
    def match_time(self, scheduled_time, current_time):
        if scheduled_time["hour"] == current_time.tm_hour and scheduled_time["minute"] == current_time.tm_min and (1 << current_time.tm_wday) & scheduled_time["wday"]:
            return True
        else:
            return False
            
    def is_same_minute(self, last_run_time, current_time):
        if last_run_time.tm_year == current_time.tm_year and last_run_time.tm_mon == current_time.tm_mon \
            and last_run_time.tm_mday == current_time.tm_mday and last_run_time.tm_hour == current_time.tm_hour \
            and last_run_time.tm_min == current_time.tm_min:
            return True
        else:
            return False
    
    def add_schedule(self, hour, minute, week, job_name, worker_type, job_cmd, job_para_list):
        scheduled_time = {"hour": hour, "minute": minute, "wday": week}
        job = ClusterJob(job_name, job_cmd, job_para_list)
        create_time = time.time()
        job.create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(create_time))
        job.job_id = int(create_time)
        scheduled_task = {"time": scheduled_time, "job": job, "last_run_time":time.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")}
        self.schedule_list.append(scheduled_task)
        print "scheduled task added: " + str(hour) + ":" + str(minute) + "----" + job_name
    
def main():
    config = ConfigParser.ConfigParser()
    config.read("conf.ini")
    ip = config.get("master configuration", "ip")
    port = int(config.get("master configuration", "listening port"))
    job_queue_size = int(config.get("master configuration", "job queue size"))
    heart_beat_interval = int(config.get("master configuration", "heart beat interval"))
    master = Master(ip, port, job_queue_size, heart_beat_interval)
    
    #pdb.set_trace()
    # 测试用
    #job = ClusterJob('test2', "IE", "test2", [{"type":"file", "path":"D:\\project\\fengzhiji\\test.txt"}])
    #master.add_job(job)
    #time.sleep(2)
    #master.add_job_by_para('test1', "IE", "test1", [{"type":"file", "path":"D:\\project\\fengzhiji\\test.txt"}])
    #master.add_schedule(6, 53, 127, "scheduled", "IE", "scheduled", [{"type":"file", "path":"I:\\project\\fengzhiji\\test.txt"}])
    #time.sleep(2)
    #master.add_schedule(6, 54, 127, "scheduled", "IE", "scheduled", [{"type":"file", "path":"I:\\project\\fengzhiji\\test.txt"}])
    #time.sleep(2)
    #master.add_schedule(6, 55, 127, "scheduled", "IE", "scheduled", [{"type":"file", "path":"I:\\project\\fengzhiji\\test.txt"}])
    #time.sleep(2)
    #master.add_schedule(6, 56, 127, "scheduled", "IE", "scheduled", [{"type":"file", "path":"I:\\project\\fengzhiji\\test.txt"}])
    master.run()
    
main()
