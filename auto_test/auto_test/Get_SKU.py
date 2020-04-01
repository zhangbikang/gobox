# -*- coding: UTF-8 -*-#-*- coding: UTF-8 -*-
import sys
import os
import json
import re
import time
import paramiko
from auto_test.write_job_suite import operator_suite_log

class gpa_operation():
    def __init__(self,env):
        self.env=env
    def cp_sku(self,**date):
        dev_id=(date["dev_id"])
        layer_org=date["layer_org"]
        layer_1_org_date=layer_org[0]
        layer_2_org_date = layer_org[1]
        layer_3_org_date = layer_org[2]
        layer_4_org_date = layer_org[3]
        open_goods_code_layer_1_date = []
        open_goods_code_layer_2_date = []
        open_goods_code_layer_3_date = []
        open_goods_code_layer_4_date = []
        close_goods_code_layer_1_date = []
        close_goods_code_layer_2_date = []
        close_goods_code_layer_3_date = []
        close_goods_code_layer_4_date = []
        save_log = operator_suite_log("auto_test_log", "AS_Get_SKU")
        for lp in range(5):
            try:
                hostid = "m.vegcloud.tech"
                pwd = "Ustaff201"
                sshname = "linaro"
                if len(str(dev_id)) == 5:
                    sshid = dev_id
                else:
                    sshid = "2" + str(dev_id)
                myclient = paramiko.SSHClient()
                myclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                myclient.connect(hostid, port=int(sshid), username=sshname, password=pwd, allow_agent=False,
                                 look_for_keys=False)
                time.sleep(5)
                stdin, stdout, stderr = myclient.exec_command("sudo bash")
                time.sleep(2)
            except:
                time.sleep(10)
            else:
                case_tm = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                trans_id = int(case_tm.replace("-", ""))
                while True:
                    cmd_open_door = "curl -X POST \\" + "http://localhost:8086/door/1/open \\" + "-H \'Content-Type: application/json\' \\" + "-H \'Postman-Token: bb06b4e0-9459-40a4-b875-b39354cbb18a\' \\" + "-H \'cache-control: no-cache\' \\" + "-d \'{\"transid\":" + '"' + str(
                        trans_id) + '"' + ",\"lockid\": \"1-1-1\",\"user_type\": 1}\'"
                    stdin, stdout, stderr = myclient.exec_command(cmd_open_door)
                    time.sleep(40)
                    cmd = "cat " + "/vbg/root/weighcv-as/log/" + str(trans_id) + ".txt"
                    stdin, stdout, stderr = myclient.exec_command(cmd)
                    trans_id += 1
                    close_door = False
                    case_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    while True:
                        line = stdout.readline()
                        if line:
                            if not close_door:
                                detect_close_door = re.findall("ASGetLockChgDetectGoods:", line)
                                open_detect_goods_layer_1 = re.findall \
                                    ("DoObjDetect OpenObjDetectInfo weId: 010101 detectinfo= (.*),\"positioninfo\"",
                                     line)
                                open_detect_goods_layer_2 = re.findall \
                                    ("DoObjDetect OpenObjDetectInfo weId: 010201 detectinfo= (.*),\"positioninfo\"",
                                     line)
                                open_detect_goods_layer_3 = re.findall \
                                    ("DoObjDetect OpenObjDetectInfo weId: 010301 detectinfo= (.*),\"positioninfo\"",
                                     line)
                                open_detect_goods_layer_4 = re.findall \
                                    ("DoObjDetect OpenObjDetectInfo weId: 010401 detectinfo= (.*),\"positioninfo\"",
                                     line)
                                close_detect_goods_layer_1 = re.findall \
                                    ("DoObjDetect CloseObjDetectInfo weId: 010101 detectinfo= (.*),\"positioninfo\"",
                                     line)
                                close_detect_goods_layer_2 = re.findall \
                                    ("DoObjDetect CloseObjDetectInfo weId: 010201 detectinfo= (.*),\"positioninfo\"",
                                     line)
                                close_detect_goods_layer_3 = re.findall \
                                    ("DoObjDetect CloseObjDetectInfo weId: 010301 detectinfo= (.*),\"positioninfo\"",
                                     line)
                                close_detect_goods_layer_4 = re.findall \
                                    ("DoObjDetect CloseObjDetectInfo weId: 010401 detectinfo= (.*),\"positioninfo\"",
                                     line)
                                if detect_close_door:
                                    close_door = True
                                if open_detect_goods_layer_1:
                                    open_goods_code_layer_1_date_org = open_detect_goods_layer_1[0]
                                    open_goods_code_layer_1_date = re.findall("\"goodsname\":(.*?),\"goodsnum\":(\d+)"
                                                                              , open_goods_code_layer_1_date_org)
                                if open_detect_goods_layer_2:
                                    open_goods_code_layer_2_date_org = open_detect_goods_layer_2[0]
                                    open_goods_code_layer_2_date = re.findall("\"goodsname\":(.*?),\"goodsnum\":(\d+)"
                                                                              , open_goods_code_layer_2_date_org)
                                if open_detect_goods_layer_3:
                                    open_goods_code_layer_3_date_org = open_detect_goods_layer_3[0]
                                    open_goods_code_layer_3_date = re.findall("\"goodsname\":(.*?),\"goodsnum\":(\d+)"
                                                                              , open_goods_code_layer_3_date_org)
                                if open_detect_goods_layer_4:
                                    open_goods_code_layer_4_date_org = open_detect_goods_layer_4[0]
                                    open_goods_code_layer_4_date = re.findall("\"goodsname\":(.*?),\"goodsnum\":(\d+)"
                                                                              , open_goods_code_layer_4_date_org)
                                if close_detect_goods_layer_1:
                                    close_goods_code_layer_1_date_org = close_detect_goods_layer_1[0]
                                    close_goods_code_layer_1_date = re.findall("\"goodsname\":(.*?),\"goodsnum\":(\d+)"
                                                                               , close_goods_code_layer_1_date_org)
                                if close_detect_goods_layer_2:
                                    close_goods_code_layer_2_date_org = close_detect_goods_layer_2[0]
                                    close_goods_code_layer_2_date = re.findall("\"goodsname\":(.*?),\"goodsnum\":(\d+)"
                                                                               , close_goods_code_layer_2_date_org)
                                if close_detect_goods_layer_3:
                                    close_goods_code_layer_3_date_org = close_detect_goods_layer_3[0]
                                    close_goods_code_layer_3_date = re.findall("\"goodsname\":(.*?),\"goodsnum\":(\d+)"
                                                                               , close_goods_code_layer_3_date_org)
                                if close_detect_goods_layer_4:
                                    close_goods_code_layer_4_date_org = close_detect_goods_layer_4[0]
                                    close_goods_code_layer_4_date = re.findall("\"goodsname\":(.*?),\"goodsnum\":(\d+)"
                                                                               , close_goods_code_layer_4_date_org)
                        else:
                            break
                    for i in range(len(open_goods_code_layer_1_date)):
                        for key, value in layer_1_org_date.items():
                            if str(key) == open_goods_code_layer_1_date[i][0].replace('"', ""):
                                if int(value) != int(open_goods_code_layer_1_date[i][1]):
                                    save_log.write_case(dev_id, "layer_1_open_sku", str(trans_id),
                                                        str(open_goods_code_layer_1_date), case_time)
                    for i in range(len(close_goods_code_layer_1_date)):
                        for key, value in layer_1_org_date.items():
                            if str(key) == close_goods_code_layer_1_date[i][0].replace('"', ""):
                                if int(value) != int(close_goods_code_layer_1_date[i][1]):
                                    save_log.write_case(dev_id, "layer_1_close_sku", str(trans_id),
                                                        str(close_goods_code_layer_1_date), case_time)
                    for i in range(len(open_goods_code_layer_2_date)):
                        for key, value in layer_2_org_date.items():
                            if str(key) == open_goods_code_layer_2_date[i][0].replace('"', ""):
                                if int(value) != int(open_goods_code_layer_2_date[i][1]):
                                    save_log.write_case(dev_id, "layer_2_open_sku", str(trans_id),
                                                        open_goods_code_layer_2_date,
                                                        case_time)
                    for i in range(len(close_goods_code_layer_2_date)):
                        for key, value in layer_2_org_date.items():
                            if str(key) == close_goods_code_layer_2_date[i][0].replace('"', ""):
                                if int(value) != int(close_goods_code_layer_2_date[i][1]):
                                    save_log.write_case(dev_id, "layer_2_close_sku", str(trans_id),
                                                        str(close_goods_code_layer_2_date), case_time)
                    for i in range(len(open_goods_code_layer_3_date)):
                        for key, value in layer_3_org_date.items():
                            if str(key) == open_goods_code_layer_3_date[i][0].replace('"', ""):
                                if int(value) != int(open_goods_code_layer_3_date[i][1]):
                                    save_log.write_case(dev_id, "layer_3_open_sku", str(trans_id),
                                                        str(open_goods_code_layer_3_date), case_time)
                    for i in range(len(close_goods_code_layer_3_date)):
                        for key, value in layer_3_org_date.items():
                            if str(key) == close_goods_code_layer_3_date[i][0].replace('"', ""):
                                if int(value) != int(close_goods_code_layer_3_date[i][1]):
                                    save_log.write_case(dev_id, "layer_3_close_sku", str(trans_id),
                                                        str(close_goods_code_layer_3_date), case_time)
                    for i in range(len(open_goods_code_layer_4_date)):
                        for key, value in layer_4_org_date.items():
                            if str(key) == open_goods_code_layer_4_date[i][0].replace('"', ""):
                                if int(value) != int(open_goods_code_layer_4_date[i][1]):
                                    save_log.write_case(dev_id, "layer_4_open_sku", str(trans_id),
                                                        str(open_goods_code_layer_4_date), case_time)
                    for i in range(len(close_goods_code_layer_4_date)):
                        for key, value in layer_4_org_date.items():
                            if str(key) == close_goods_code_layer_4_date[i][0].replace('"', ""):
                                if int(value) != int(close_goods_code_layer_4_date[i][1]):
                                    save_log.write_case(dev_id, "layer_4_close_sku", str(trans_id),
                                                        str(close_goods_code_layer_4_date), case_time)
                    time.sleep(100)
        print(str(lp)+"次SSH登入失败")

