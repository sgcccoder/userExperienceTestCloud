#!python
#coding=utf8
from SimpleXMLRPCServer import SimpleXMLRPCServer
import xmlrpclib
import thread
import time
import os
import ConfigParser
import pdb
from auto import Auto

executor = Auto()

class Slave:
    def __init__(self, ip, port, worker_type, master_url):
        self.port   = port
        self.ip     = ip
        self.status = 0     #0是空闲，1是忙碌，2是异常，99是关闭
        self.worker_type = worker_type
        self.master_url = master_url
        self.heart_beat_interval = 0
        self.server = SimpleXMLRPCServer((ip, self.port))
        self.server.register_multicall_functions()
        self.server.register_function(self.work, "work")
        self.server.register_function(self.stop, "stop")
        self.master_proxy = xmlrpclib.ServerProxy(self.master_url)
        self.dic_worker_cmd = {}
        
    def getProxy(self):
        return self.master_proxy
        
    def run(self):
        #pdb.set_trace()
        (my_worker_id, self.heart_beat_interval) = self.master_proxy.register(self.ip, self.port, self.status, self.worker_type)
        print "I am a " + self.worker_type + " worker. My work_id is " + str(my_worker_id)
        thread.start_new_thread(self.send_heart_beat, ())
        return self.server.serve_forever()
    
    def stop(self):
        self.server.server_close()
        self.status = 99
        return 0

    def prepare_parameter(self, job_id, para_list):
        for para in para_list:
            if para["type"] == "file":
                file_path = "receive_files" + os.path.sep + str(job_id) + os.path.sep
                file_name = para["path"]
                index = para["path"].rfind(os.path.sep)
                print "index: " + str(index)
                if (index != -1):
                    #file_path += para["path"][0:index + 1]
                    file_name = para["path"][index + 1:]
                try:
                    print file_path
                    os.makedirs(file_path)
                except:
                    print "create directory failed!"
                handle = open(file_path + file_name, "wb")
                handle.write(self.master_proxy.get_file(para["path"]).data)
                handle.close()                
                para["path"] = file_path + file_name
    
    def work(self, job_id, job_cmd, para_list):
        print "run job_" + str(job_id) + ":" + str(para_list)
        try:
            self.prepare_parameter(job_id, para_list)
            thread.start_new_thread(self.run_a_job, (job_id, job_cmd, para_list))
            self.status = 1
            print self.ip + " is " + str(self.status)
            self.master_proxy.update_status(self.ip, self.status)
        except:
            return -1
        return job_id
    
    def run_a_job(self, job_id, job_cmd, parameter):
        print "start, " + str(job_cmd) + ":" + str(parameter)
        if (self.dic_worker_cmd.has_key(job_cmd)):
            self.dic_worker_cmd[job_cmd](parameter)
        time.sleep(30)
        self.status = 0
        print "finish, " + str(job_cmd) + ":" + str(parameter)
    
    def send_heart_beat(self):
        while self.status != 99:
            print "send heart_beat"
            time.sleep(self.heart_beat_interval)
            self.master_proxy.heart_beat(self.ip, self.status)
        else:
            self.master_proxy.update_status(self.ip, self.status)
            
    def register_func(self, cmd, func):
        if (self.dic_worker_cmd.has_key(cmd)):
            return -1
        self.dic_worker_cmd[cmd] = func
        return 0

def Main():
    config = ConfigParser.ConfigParser()
    config.read("conf.ini")
    ip = config.get("slave configuration", "ip address")
    port = int(config.get("slave configuration", "listening port"))
    worker_type = config.get("slave configuration", "worker type")
    master_url = config.get("slave configuration", "master url")
    print master_url
    slave = Slave(ip, port, worker_type, master_url)
    slave.register_func('exec', executor.inspect)
    slave.run()

Main()
