# -*- coding: UTF-8 -*-#-*- coding: UTF-8 -*-
import urllib
from http import cookiejar
import json
import time
import pymysql
import random
from auto_test.Create_Weight import create_weight
from auto_test.write_job_suite import operator_suite_log
from auto_test.mERP_Operation import mERP_operation


class wifi_auto_test():
    def __init__(self,url,login_name,login_pw,env,db_name, job_name):
        self.mERP=mERP_operation(str(url), str(login_name), str(login_pw),int(env))
        self.save_log=operator_suite_log(str(db_name), str(job_name))

    def devid_wifi_config(self, dev_id):
        # 配置wifi链接uSTAR_Public_2.4G
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        ssid = "uSTAR_Public_2.4G"
        pw = "uSTAR2019@"
        # 查询WiFi和可连接的list
        config_wifi_org = self.mERP.query_wifi_dev(dev_id)
        config_wifi_status = config_wifi_org[0]
        config_wifi_list_org = self.mERP.query_wifi_ap(dev_id)
        config_wifi_list = config_wifi_list_org[1]
        # 是否查询成功
        if config_wifi_status == "Pass":
            # list里面是否有前文需要连接的SSID
            if ssid in config_wifi_list["ssid_list"]:
                config_wifi_connect = self.mERP.connect_wifi(dev_id, ssid, pw)
                config_wifi_connect_return = config_wifi_connect[0]
                time.sleep(10)
                if config_wifi_connect_return == "Pass":
                    n = 0
                    while n < 5:
                        config_wifi_connect_org = self.mERP.query_wifi_dev(dev_id)
                        config_wifi_connect_status = config_wifi_connect_org[1]
                        time.sleep(10)
                        # 查询是否在连接中
                        if config_wifi_connect_status == "RRPC_TIMEOUT":
                            time.sleep(60)
                            n += 1
                        else:
                            self.save_log.write_case(dev_id, "connect_wifi_no_rrpc_timeout", "Fail",config_wifi_connect_org[1], case_tm)
                            break
                    # 重新查询
                    query_wifi_connect1 = self.mERP.query_wifi_dev(dev_id)
                    query_wifi_connect1_status = query_wifi_connect1[0]
                    query_wifi_connect2 = self.mERP.query_save_ssid(dev_id)
                    query_wifi_connect2_status = query_wifi_connect2[0]
                    if query_wifi_connect1_status == "Pass" and query_wifi_connect2_status == "Pass":
                        if query_wifi_connect1[1]["state"] == "connected" and query_wifi_connect2[1]["ssid_list"] == ["uSTAR_Public_2.4G"]:
                            self.save_log.write_case(dev_id, "connect_uSTAR_wifi", "Pass", "Pass", case_tm)
                        else:
                            self.save_log.write_case(dev_id, "connect_uSTAR_wifi", "Fail", query_wifi_connect1[1],case_tm)
                    else:
                        self.save_log.write_case(dev_id, "connect_wifi_query", "Fail", query_wifi_connect1[1], case_tm)
                else:
                    self.save_log.write_case(dev_id, "connect_wifi", "Fail", config_wifi_connect[1], case_tm)
            else:
                self.save_log.write_case(dev_id, "connect_wifilist_no_uSTAR_wifi", "Fail", "no_ssid", case_tm)
        else:
            self.save_log.write_case(dev_id, "connect_wifi_query", "Fail", config_wifi_list, case_tm)
        time.sleep(10)
        # 切断wifi#
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_wifi_disconnect = self.mERP.disconnect_wifi(dev_id)
        config_wifi_disconnect_return = config_wifi_disconnect[0]
        time.sleep(10)
        if config_wifi_disconnect_return == "Pass":
            n1 = 0
            while n1 < 5:
                config_wifi_disconnect_org = self.mERP.query_wifi_dev(dev_id)
                config_wifi_disconnect_status = config_wifi_disconnect_org[1]
                time.sleep(10)
                # 查询是否在切断中
                if config_wifi_disconnect_status == "RRPC_TIMEOUT":
                    time.sleep(60)
                    n1 += 1
                else:
                    self.save_log.write_case(dev_id, "config_wifi_disconnect", "Fail", config_wifi_disconnect_org[1],case_tm)
                    break
            # 重新查询
            query_wifi_disconnect1 = self.mERP.query_wifi_dev(dev_id)
            query_wifi_disconnect1_status = query_wifi_disconnect1[0]
            query_wifi_disconnect2 = self.mERP.query_save_ssid(dev_id)
            query_wifi_disconnect2_status = query_wifi_disconnect2[0]
            if query_wifi_disconnect1_status == "Pass" and query_wifi_disconnect2_status == "Pass":
                if query_wifi_disconnect1[1]["state"] == "disconnected" and query_wifi_disconnect2[1]["ssid_list"] == []:
                    self.save_log.write_case(dev_id, "disconnect_wifi", "Pass", "Pass", case_tm)
                else:
                    self.save_log.write_case(dev_id, "disconnect_wifi", "Fail", query_wifi_disconnect1[1], case_tm)
            else:
                self.save_log.write_case(dev_id, "disconnect_wifi_query", "Fail", query_wifi_disconnect1[1], case_tm)
        else:
            self.save_log.write_case(dev_id, "no_disconnect_wifi", "Fail", config_wifi_disconnect[1], case_tm)
        time.sleep(10)
        # 禁用wifi#
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_wifi_disable = self.mERP.disable_wifi(dev_id)
        if config_wifi_disable[0] == "Pass":
            time.sleep(60)
            query_wifi_disable = self.mERP.query_wifi_dev(dev_id)
            if query_wifi_disable[0] == "Pass":
                if query_wifi_disable[1]["state"] == "unavailable":
                    self.save_log.write_case(dev_id, "disable_wifi", "Pass", "Pass", case_tm)
                else:
                    self.save_log.write_case(dev_id, "disable_wifi", "Fail", query_wifi_disable[1], case_tm)
            else:
                self.save_log.write_case(dev_id, "disable_wifi_query", "Fail", query_wifi_disable[1], case_tm)
        else:
            self.save_log.write_case(dev_id, "disable_wifi", "Fail", config_wifi_disable[1], case_tm)
        time.sleep(10)
        # 开启wifi#
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        config_wifi_enable = self.mERP.enable_wifi(dev_id)
        if config_wifi_enable[0] == "Pass":
            time.sleep(60)
            query_wifi_enable1 = self.mERP.query_wifi_dev(dev_id)
            query_wifi_enable2 = self.mERP.query_save_ssid(dev_id)
            if query_wifi_enable1[0] == "Pass" and query_wifi_enable2[0] == "Pass":
                if query_wifi_enable1[1]["state"] == "disconnected" and query_wifi_enable2[1]["ssid_list"] == []:
                    self.save_log.write_case(dev_id, "enable_wifi", "Pass", "Pass", case_tm)
                else:
                    self.save_log.write_case(dev_id, "enable_wifi", "Fail", query_wifi_enable1[1], case_tm)
            else:
                self.save_log.write_case(dev_id, "enable_wifi_query", "Fail", query_wifi_enable1[1], case_tm)
        else:
            self.save_log.write_case(dev_id, "enable_wifi", "Fail", config_wifi_enable[1], case_tm)


