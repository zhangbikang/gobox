#-*- coding: UTF-8 -*-#-*- coding: UTF-8 -*-
import sys
import json
import re
import time
import paramiko
import pymysql
import datetime
import urllib
from http import cookiejar
import requests

class get_performance():
    def __init__(self,union_id,dev_id,url,db_name,sshid,sshname):
        self.union_id=union_id
        self.dev_id=dev_id
        self.url=url
        self.db_name=db_name
        self.sshid=int(sshid)
        self.sshname=str(sshname)

    def start_app(self):
        try:

            payload = "{\"devname\": \"" + self.union_id + "\",\"req\": {\"A\": 152,\"P\": {\"appname\": \" frp-client-ssh \",\"action\": 4,\"port\":\"" + str(self.dev_id) + "\"}}}"
            headers = {'Content-Type': "application/json", 'cache-control': "no-cache",
                       'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7"}
            response = requests.request("POST", self.url, data=payload, headers=headers)
            app_start_org = json.loads(response.text)
            if app_start_org["msg"].lower() == "success":
                pid_id=app_start_org["output"]["pid"]
            else:
                return "FRP 开启查询失败"
        except:
            return ("开启FRP API下发失败")
        for i in range(20):
            try:
                payload_pid = "{\"devname\": \"" + self.union_id + "\",\"req\": { \"A\": 153,\"P\": {\"pid\":\"" + str(pid_id) + "\"}}}"
                headers_pid = {'Content-Type': "application/json", 'cache-control': "no-cache",
                           'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7"}
                response_pid = requests.request("POST", self.url, data=payload_pid, headers=headers_pid)
                app_status_org = json.loads(response_pid.text)
                if app_status_org["msg"].lower() == "success":
                    if app_status_org["output"]["state"]=="completed":
                        return "Pass"
            except:
                return ("PID 查询PAI下发失败")
            time.sleep(5)
        return "FRP开启失败"

    def get_date(self):
        ssh_repeat = 0
        while True:
            try:
                hostid = "m.vegcloud.tech"
                pwd = "Ustaff201"
                myclient = paramiko.SSHClient()
                myclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                myclient.connect(hostid, port=self.sshid, username=self.sshname, password=pwd, allow_agent=False,
                                 look_for_keys=False)
                time.sleep(5)
                stdin, stdout, stderr = myclient.exec_command("sudo bash")
                time.sleep(2)
                stdin, stdout, stderr = myclient.exec_command("top -b -n 1")
                time.sleep(2)
            except:
                ssh_repeat += 1
                if ssh_repeat > 5:
                    myclient.close()
                    return ("SSH登入失败")
                time.sleep(10)
            else:
                break
        try:
            check_list = ["door", "iotkit", "apps", "alarm", "monitor", "tts"]
            cpu_used = {'door': 0, 'weigh': 0, "weighcv_cm": 0, "weighcv_as": 0, "iotkit": 0, "apps": 0, "alarm": 0,
                        "monitor": 0, "tts": 0}
            mem_used = {'door': 0, 'weigh': 0, "weighcv_cm": 0, "weighcv_as": 0, "iotkit": 0, "apps": 0, "alarm": 0,
                        "monitor": 0, "tts": 0}
            mem_summary = {'mem_total': 0, 'mem_free': 0, 'mem_use': 0, 'mem_buff': 0, 'remaind_space': 0}
            while True:
                line = stdout.readline()
                if line:
                    pattern_apps = re.compile("(\S+)\s+(\S+)\s+\S+\s+(\S+)$")
                    pattern_mem = re.compile(
                        "KiB Mem :\s+(\d+)\s+total,\s+(\d+)\s+free,\s+(\d+)\s+used,\s+(\d+)\s+buff/cache")
                    top_all_org = pattern_apps.findall(line)
                    top_mem_org = pattern_mem.findall(line)
                    if top_all_org:
                        top_all = top_all_org[0]
                        for i in range(len(check_list)):
                            if top_all[2] == check_list[i]:
                                cpu_used[check_list[i]] = str(top_all[0])
                                mem_used[check_list[i]] = str(top_all[1])
                                break
                    if top_mem_org:
                        top_mem = top_mem_org[0]
                        if len(top_mem) == 4:
                            mem_summary["mem_total"] = int(top_mem[0]) // 1024
                            mem_summary["mem_free"] = int(top_mem[1]) // 1024
                            mem_summary["mem_use"] = int(top_mem[2]) // 1024
                            mem_summary["mem_buff"] = int(top_mem[3]) // 1024
                else:
                    break
        except:
            return ("CPU和mem匹配数据失败")
        try:
            stdin, stdout, stderr = myclient.exec_command("df -h")
            time.sleep(2)
            if self.sshname == "linaro":
                while True:
                    line_space = stdout.readline()
                    if line_space:
                        pattern_space = re.compile("/dev/root\s+\S+\s+\S+\s+\S+\s+(\d+)")
                        remaind_space_org = pattern_space.findall(line_space)
                        if remaind_space_org:
                            mem_summary["remaind_space"] = int(remaind_space_org[0])
                    else:
                        return (cpu_used, mem_used, mem_summary)
            elif self.sshname == "pi":
                while True:
                    line_space = stdout.readline()
                    if line_space:
                        pattern_space = re.compile("/dev/mmcblk0p2\s+\S+\s+\S+\s+\S+\s+(\d+)")
                        remaind_space_org = pattern_space.findall(line_space)
                        if remaind_space_org:
                            mem_summary["remaind_space"] = int(remaind_space_org[0])
                    else:
                        return (cpu_used, mem_used, mem_summary)
        except:
            return ("Summary获取失败")
        myclient.close()
        return True