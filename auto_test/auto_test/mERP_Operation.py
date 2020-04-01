#-*- coding: UTF-8 -*-#-*- coding: UTF-8 -*-
import urllib
from http import cookiejar
import json
import time
import pymysql
import random
class mERP_operation():
    def __init__(self,url,user,password,env):
        if env ==0:
            self.url_login = "http://" + url + ":8080/login"
            self.url_add_goods = "http://" + url + ":8080/sku-mgmt"
            self.url_query_box = "http://" + url + ":8080/post_common_admin/"
            self.url_query_box_info = "http://" + url + ":8080/box-mgmt/"
            self.url_wifi = "http://" + url + ":8080/network/"
            self.url_monitor = "http://" + url + ":8080/monitor"
            self.url_rf = "http://" + url + ":8080/main"
            self.url_post_common = "http://" + url + ":8080/post_common_admin/"
            self.url_box_mgmt = "http://" + url + ":8080/box-mgmt"
            self.url_weigh_type = "http://" + url + ":8080/update_dev_weigh_type"
            self.url_alarm="http://"+ url + ":8080/alarm/"
        elif env ==1:
            self.url_login = "https://" + url + "/login"
            self.url_add_goods = "https://" + url + "/sku-mgmt"
            self.url_query_box = "https://" + url + "/post_common_admin/"
            self.url_query_box_info = "https://" + url + "/box-mgmt/"
            self.url_wifi = "https://" + url + "/network/"
            self.url_monitor = "https://" + url + "/monitor"
            self.url_rf = "https://" + url + "/main"
            self.url_post_common = "https://" + url + "/post_common_admin/"
            self.url_box_mgmt = "https://" + url + "/box-mgmt"
            self.url_weigh_type = "https://" + url + "/update_dev_weigh_type"
            self.url_alarm="https://"+url+"/alarm/"
        self.login_user=user
        self.login_pw=password
        cj = cookiejar.CookieJar()
        cookie_support = urllib.request.HTTPCookieProcessor(cj)
        opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
        urllib.request.install_opener(opener)
        self.headers = {'Connection': 'keep-alive',
                        'Content-Type': 'application/json',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
        self.token=self.login()
    def commit_post(self,url,postDate):
        try:
            #postData = urllib.parse.urlencode(postDate).encode('utf-8')
            #print(postData)
            postDate=json.dumps(postDate)
            postDate=bytes(postDate,'utf-8')
            request_result = urllib.request.Request(url, postDate, self.headers)
            #print(request_result)
            request_result = urllib.request.urlopen(request_result)
            response_date_org = request_result.read().decode()
            response_date = json.loads(response_date_org)
            return response_date
        except:
            return "post 提交失败"
    def login(self):
        try:
            postData= {'employee_id': self.login_user, 'employee_pass': self.login_pw}
            token_org=self.commit_post(self.url_login,postData)
            return token_org["token"]
        except:
            return "登入失败"
    def query_goods(self):
        try:
            postData = {'access_token': self.token, 'command': "query_sku","jwtauth_auth_ret_type": "json"}
            query_goods_org=self.commit_post(self.url_post_common,postData)
            if query_goods_org["msg"].lower()=="success" and int(query_goods_org["nums"])>0:
                return ("Pass",query_goods_org["output"])
            else:
                return ("Fail",query_goods_org["msg"])
        except:
            return "查询商品失败"
    def add_goods(self,barcode,base_weight,drift_weight):
        try:
            postData = {'access_token': self.token, 'barcode': barcode, 'brand': "ustar", 'category': "酒水饮料",
                        'command': "AddSku", 'cost': "0.01", 'is_standard': "True", 'jwtauth_auth_ret_type': "json",
                        'name': "测试商品", 'price': "0.01", 'short_name': "测试商品", 'spec': "500ml/瓶", 'unit': "瓶",
                        'weight': str(base_weight), 'weight_drift': str(drift_weight)}

            add_goods_result = self.commit_post(self.url_add_goods, postData)

            if add_goods_result["msg"].lower() == "success":
                return ("Pass",add_goods_result["output"])
            else:
                return ("Fail",add_goods_result["msg"])
        except:
            "添加商品失败"
    def update_goods(self,**args):
        try:
            postData = {'access_token': self.token, 'command': "UpdateSku",'jwtauth_auth_ret_type': "json"}
            for key,value in args.items():
                postData[key]=value
            update_sku_result=self.commit_post(self.url_add_goods,postData)
            if update_sku_result["msg"].lower()=="success":
                return ("Pass",update_sku_result["output"])
            else:
                return ("Fail",update_sku_result["msg"])
        except:
            return "更新商品信息失败"
    def update_stock(self,barcode,opt,num):
        try:
            # opt 1表示入库，2表示出库
            postData = {'access_token': self.token, 'barcode': str(barcode), 'command': "update_stock", 'dev_id': 1,
                        'jwtauth_auth_ret_type': "json", 'memo': "更新仓存", 'num': str(num), 'operation': str(opt),
                        'pos': "010101", 'union_id': ""}
            update_stock_status=self.commit_post(self.url_post_common,postData)
            if update_stock_status["msg"].lower()=="success":
                return ("Pass",update_stock_status["msg"])
            else:
                return ("Fail",update_stock_status["msg"])
        except:
            return "更新库存失败"
    def delete_goods(self,*barcode):
        try:
            postData = {'access_token': self.token, "barcode_list":barcode, 'command': "DelSku",'jwtauth_auth_ret_type': "json"}
            delete_goods_status=self.commit_post(self.url_add_goods,postData)
            if delete_goods_status["msg"].lower()=="success":
                return ("Pass",delete_goods_status["output"])
            else:
                return ("Fail",delete_goods_status["msg"])
        except:
            return "删除商品失败"
    def query_box(self):
        try:
            postData = {'access_token': self.token, 'command': "query_dev_info_sync", 'jwtauth_auth_ret_type': "json"}
            query_box_status=self.commit_post(self.url_post_common,postData)
            if query_box_status["msg"].lower()=="success"and int(query_box_status["nums"])>0:
                return ("Pass",query_box_status["output"])
            else:
                return ("Fail",query_box_status["msg"])
        except:
            return "查询货柜信息失败"
    def query_dev_detailinfo(self,dev_id):
        try:
            postDate={"access_token": self.token, "jwtauth_auth_ret_type": "json", "dev_id": dev_id,"command": "QueryInfoDetail"}
            query_dev_info_status=self.commit_post(self.url_box_mgmt,postDate)
            if query_dev_info_status["msg"].lower()=="success":
                return ("Pass",query_dev_info_status["output"])
            else:
                return ("Fail",query_dev_info_status["msg"])
        except:
            return "查询货柜信息失败"
    def update_dev_detailinfo(self,**arg):
        try:
            postDate={"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "UpdateDevInfo"}
            for key,value in arg.items():
                postDate[key]=value
            set_dev_info_status = self.commit_post(self.url_box_mgmt, postDate)
            if set_dev_info_status["msg"].lower()=="success":
                return ("Pass",set_dev_info_status["output"])
            else:
                return ("Fail",set_dev_info_status["msg"])
        except:
            return "更新货柜信息失败"
    def query_dev_AudioConfig(self,dev_id):
        try:
            postDate={"access_token": self.token, "jwtauth_auth_ret_type": "json", "dev_id": int(dev_id),"command": "QueryAudioConfig"}
            query_dev_audio_status=self.commit_post(self.url_query_box_info,postDate)
            if query_dev_audio_status["msg"].lower()=="success":
                return ("Pass",query_dev_audio_status["output"])
            else:
                return ("Fail",query_dev_audio_status["msg"])
        except:
            return "查询货柜语言信息失败"
    def set_dev_AudioConfig(self,dev_id,play_type):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "UpdateAudioConfig","dev_id": int(dev_id), "config": play_type}
            set_audio_result=self.commit_post(self.url_query_box_info,postData)
            if set_audio_result["msg"].lower()=="success":
                return ("Pass",set_audio_result["output"])
            else:
                return ("Fail",set_audio_result["msg"])
        except:
            return "配置语音提示失败"
    def query_wifi_dev(self,dev_id):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "QueryWifiDev","dev_id": dev_id}
            query_wifi_dev_status=self.commit_post(self.url_wifi,postData)
            if query_wifi_dev_status["msg"].lower()=="success":
                return ("Pass",query_wifi_dev_status["output"])
            else:
                return ("Fail",query_wifi_dev_status["msg"])
        except:
            return "查询wifi信息失败"
    def query_wifi_ap(self,dev_id):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "QueryWifiAp","dev_id": dev_id}
            query_wifi_ap_status=self.commit_post(self.url_wifi,postData)
            if query_wifi_ap_status["msg"].lower()=="success":
                return ("Pass",query_wifi_ap_status["output"])
            else:
                return ("Fail",query_wifi_ap_status["msg"])
        except:
            return "查询wifi信息失败"
    def query_save_ssid(self,dev_id):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "QuerySavedWifiSsid","dev_id": dev_id}
            query_wifi_save_ssid=self.commit_post(self.url_wifi,postData)
            if query_wifi_save_ssid["msg"].lower()=="success":
                return ("Pass",query_wifi_save_ssid["output"])
            else:
                return ("Fail",query_wifi_save_ssid["msg"])
        except:
            return "查询wifi信息失败"
    def connect_wifi(self,dev_id,ssid,pw):
        try:
            postData = {'access_token': self.token, 'command': "ConnWifiAp", 'dev_id': dev_id,'jwtauth_auth_ret_type': "json", 'password': pw, 'ssid': ssid}
            connect_result = self.commit_post(self.url_wifi, postData)
            if connect_result["msg"].lower() == "rrpc_timeout":
                return ("Pass",connect_result["code"])
            else:
                return ("Fail",connect_result["msg"])
        except:
            return "连接wifi失败"
    def disconnect_wifi(self,dev_id):
        try:
            postData = {'access_token': self.token, 'command': "EnableWifiConn", 'connect':False,'dev_id': dev_id, 'jwtauth_auth_ret_type': "json"}
            disconnect_status=self.commit_post(self.url_wifi,postData)
            if disconnect_status["msg"].lower()=="rrpc_timeout":
                return ("Pass",disconnect_status["code"])
            else:
                return ("Fail",disconnect_status["msg"])
        except:
            return "断开wifi失败"
    def disable_wifi(self, dev_id):
        try:
            postData = {'access_token': self.token, 'command': "EnableWifi", 'enable': False, 'dev_id': dev_id,'jwtauth_auth_ret_type': "json"}
            disable_status = self.commit_post(self.url_wifi, postData)
            if disable_status["msg"].lower() == "success":
                return ("Pass", disable_status["code"])
            else:
                return ("Fail", disable_status["msg"])
        except:
            return "禁用wifi失败"
    def enable_wifi(self, dev_id):
        try:
            postData = {'access_token': self.token, 'command': "EnableWifi", 'enable': True, 'dev_id': dev_id,'jwtauth_auth_ret_type': "json"}
            enable_status = self.commit_post(self.url_wifi, postData)
            if enable_status["msg"].lower() == "success":
                return ("Pass", enable_status["code"])
            else:
                return ("Fail", enable_status["msg"])
        except:
            return "开启wifi失败"
    def query_monitor(self,dev_id):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "QueryCam","dev_id": dev_id}
            query_monitor_status=self.commit_post(self.url_monitor,postData)
            if query_monitor_status["msg"].lower()=="success":
                return query_monitor_status["output"]
            else:
                return query_monitor_status["msg"]
        except:
            return "查询监控信息失败"
    def set_monitor_stream(self,dev_id,stream_trpe):
        try:
            postData = {"access_token": self.token,"jwtauth_auth_ret_type": "json", "dev_id": dev_id,"command": "ConfigCam", "stream_chn": int(stream_trpe)}

            set_monitor_stream_status = self.commit_post(self.url_monitor, postData)
            if set_monitor_stream_status["msg"].lower() == "success":
                return "Pass"
            else:
                return set_monitor_stream_status["msg"]
        except:
            return "设置码流失败"
    def enable_montiro(self,dev_id,mode):
        #关闭是0，打开是1
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "dev_id": dev_id,"command": "EnableSaveVideo", "mode": int(mode)}
            enable_monitor_status=self.commit_post(self.url_monitor,postData)
            if enable_monitor_status["msg"].lower()=="success":
                return "Pass"
            else:
                return enable_monitor_status["msg"]
        except:
            return "开关监控失败"
    def query_goods_store_inventory(self,starttime,endtime,**args):
        #"dev_list":List
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_stock_detail","start_date": str(starttime), "end_date": str(endtime)}
            if args:
                for key,value in args.items():
                    postData[key]=value
            query_store_inventory_result=self.commit_post(self.url_post_common,postData)
            if query_store_inventory_result["msg"]=="success":
                return ("Pass",query_store_inventory_result["output"])
            else:
                return ("Fail",query_store_inventory_result["msg"])
        except:
            return "查询仓库库存流水失败"
    def query_goods_store(self,**args):
        # "barcode_contain": str(barcode), "name": str(name)
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_sku"}
            if args:
                for key,value in args.items():
                    postData[key]=value
            query_goods_num=self.commit_post(self.url_post_common,postData)
            if query_goods_num["msg"].lower()=="success":
                return ("Pass",query_goods_num["output"])
            else:
                return ("Fail",query_goods_num["msg"])
        except:
            return "查询仓库库存失败"
    def query_goods_store_box(self,**args):
        # "dev_list":Lsit,"domain_name":str(name)
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_multi_dev_sku"}
            if args:
                for key, value in args.items():
                    postData[key] = value
            query_goods_box_all = self.commit_post(self.url_post_common, postData)
            if query_goods_box_all["msg"].lower() == "success":
                return ("Pass",query_goods_box_all["output"])
            else:
                return ("Fail",query_goods_box_all["msg"])
        except:
            return "查询柜子库存失败"
    def query_goods_box_inventory(self,starttime,endtime,**args):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_stock_detail", "start_date": str(starttime), "end_date": str(endtime)}
            if args:
                for key, value in args.items():
                    postData[key] = value
            query_goods_box_inventory_all = self.commit_post(self.url_post_common, postData)
            if query_goods_box_inventory_all["msg"].lower() == "success":
                return ("Pass",query_goods_box_inventory_all["output"])
            else:
                return ("Fail",query_goods_box_inventory_all["msg"])
        except:
            return "查询柜子库存流水失败"
    def query_trade_pack(self,starttime,endtime,**args):
        # {"province": "浙江省"，"city": "杭州市"，"district": "滨江区","dev_list": [2001],"dev_name": "cm","domain_name": "test-2001","trans_id": "‌201905090953569057","trans_status": [100],"pay_mode": [8]}
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_trade_pack","start_date": str(starttime), "end_date": str(endtime)}
            if args:
                for key,value in args.items():
                    postData[key]=value
            query_trade_status=self.commit_post(self.url_post_common,postData)
            if query_trade_status["msg"].lower()=="success":
                return ("Pass",query_trade_status["output"])
            else:
                return ("Fail",query_trade_status["msg"])
        except:
            return "查询交易订单失败"
    def query_trade_goods(self,starttime,endtime,**args):
        # {"province": "浙江省"，"city": "杭州市"，"district": "滨江区","dev_list": [2001],"dev_name": "cm","domain_name": "test-2001","trans_id": "‌201905090953569057","prod_name": "安慕希希腊风味酸奶"}
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_trade","start_date": str(starttime), "end_date": str(endtime)}
            if args:
                for key,value in args.items():
                    postData[key]=value
            query_trade_status=self.commit_post(self.url_post_common,postData)
            if query_trade_status["msg"].lower()=="success":
                return ("Pass",query_trade_status["output"])
            else:
                return ("Fail",query_trade_status["msg"])
        except:
            return "查询交易商品失败"
    def query_trade_income(self,starttime,endtime,**args):
        # {"province": "浙江省"，"city": "杭州市"，"district": "滨江区","dev_list": [2001],"dev_name": "cm","domain_name": "test-2001","trans_id": "‌201905090953569057","out_trade_no": "2019051015020838600120100018486"}
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_trade_income","start_date": str(starttime), "end_date": str(endtime)}
            if args:
                for key,value in args.items():
                    postData[key]=value
            query_trade_status=self.commit_post(self.url_post_common,postData)
            if query_trade_status["msg"].lower()=="success":
                return ("Pass",query_trade_status["output"])
            else:
                return ("Fail",query_trade_status["msg"])
        except:
            return "查询收款信息失败"
    def query_trade_refund(self,starttime,endtime,**args):
        # {"province": "浙江省"，"city": "杭州市"，"district": "滨江区","dev_list": [2001],"dev_name": "cm","domain_name": "test-2001","trans_id": "‌201905090953569057","ref_stat": [100]}
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_trade_refund","start_date": str(starttime), "end_date": endtime}
            if args:
                for key,value in args.items():
                    postData[key]=value
            query_trade_status=self.commit_post(self.url_post_common,postData)
            if query_trade_status["msg"].lower()=="success":
                return ("Pass",query_trade_status["output"])
            else:
                return ("Fail",query_trade_status["msg"])
        except:
            return "查询退款信息失败"
    def query_trade_refund_request(self,starttime,endtime,**args):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json","command": "query_user_refund_request", "start_date": str(starttime), "end_date": str(endtime)}
            if args:
                for key,value in args.items():
                    postData[key]=value
            query_trade_status=self.commit_post(self.url_post_common,postData)
            if query_trade_status["msg"].lower()=="success":
                return ("Pass",query_trade_status["output"])
            else:
                return ("Fail",query_trade_status["msg"])
        except:
            return "查询退款请求信息失败"
    def query_goods_sales_count(self,starttime,endtime):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_commodity_trade","start_date": str(starttime), "end_date": str(endtime)}
            query_goods_count_result=self.commit_post(self.url_post_common,postData)
            if query_goods_count_result["msg"].lower()=="success":
                return ("Pass",query_goods_count_result["output"])
            else:
                return ("Fail",query_goods_count_result["msg"])
        except:
            return "查询商品销售统计失败"
    def query_user_add(self,starttime,endtime,**args):
        #{"dev_list": [2001]}
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_new_user_info","start_date": str(starttime), "end_date": str(endtime)}
            if args:
                for key,value in args.items():
                    postData[key]=value
            query_user_add_result=self.commit_post(self.url_post_common,postData)
            if query_user_add_result["msg"].lower()=="success":
                return ("Pass",query_user_add_result["output"])
            else:
                return ("Fail",query_user_add_result["msg"])
        except:
            return "查询新增用户信息失败"
    def query_goods_sales_count_box(self,starttime,endtime,**args):
        # {"province": "浙江省"，"city": "杭州市"，"district": "滨江区","dev_list": [2001],"dev_name": "cm","domain_name": "test-2001","prod_code": "‌201905090953569057","prod_name": "红牛"}
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_dev_commodity_trade","start_date": str(starttime), "end_date": str(endtime)}
            if args:
                for key,value in args.items():
                    postData[key]=value
            query_goods_box_result=self.commit_post(self.url_post_common,postData)
            if query_goods_box_result["msg"].lower()=="success":
                return ("Pass",query_goods_box_result["output"])
            else:
                return ("Fail",query_goods_box_result["msg"])
        except:
            return "查询货柜商品销售信息失败"
    def query_sales_service_box(self,starttime,endtime,**args):
        # {"province": "浙江省"，"city": "杭州市"，"district": "滨江区","dev_list": [2001],"dev_name": "cm","domain_name": "test-2001"}
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json","command": "query_dev_trade_collect", "start_date": str(starttime), "end_date": str(endtime)}
            if args:
                for key,value in args.items():
                    postData[key]=value
            query_dev_trade_collect_result=self.commit_post(self.url_post_common,postData)
            if query_dev_trade_collect_result["msg"].lower()=="success":
                return ("Pass",query_dev_trade_collect_result["output"])
            else:
                return ("Fail",query_dev_trade_collect_result["msg"])
        except:
            return "查询货柜商品销售信息失败"
    def query_dev_sku(self,dev_id,union_id):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_dev_sku", "dev_id": str(dev_id), "union_id": str(union_id), "abnor": True}
            query_dev_sku_result=self.commit_post(self.url_post_common,postData)
            if query_dev_sku_result["msg"].lower()=="success":
                return ("Pass",query_dev_sku_result["output"])
            else:
                return ("Fail",query_dev_sku_result["msg"])
        except:
            return "查询货柜SKU失败"
    def operation_sku_box(self,operation_type,dev_id,union_id,barcode,pos_id,operation):
        #checklevel和operation是整数其他字符，operation_type（“add”增加商品，operation值0；"delete"删除商品，operation值 1；"update"下架商品，operation值2）
        try:
            if operation_type=="add":
                operation_command="AddSku"
            elif operation_type=="delete":
                operation_command="DelSku"
            elif operation_type=="update":
                operation_command="UpdateSku"
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "dev_id": str(dev_id),
                        "union_id": str(union_id), "command": operation_command, "pos": str(pos_id),"check_level": 1,"barcode": str(barcode), "operation": int(operation)}
            update_sku_result=self.commit_post(self.url_box_mgmt,postData)
            if update_sku_result["msg"].lower()=="success":
                return ("Pass",update_sku_result["output"])
            else:
                return ("Fail",update_sku_result["msg"])
        except:
            return "货柜添加、删除、下架商品失败"
    def update_sku_count(self,union_id,barcode,pos_id,operation,num):
        #operation为整型，0上货，1下货
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "dev_uid": str(union_id),"command": "UpdateSkuCount", "barcode": str(barcode), "pos": str(pos_id), "option": int(operation),
                    "check_weight": True, "num": str(num), "memo": "更新设备商品仓存"}
            update_sku_result=self.commit_post(self.url_box_mgmt,postData)
            if update_sku_result["msg"].lower()=="success":
                return ("Pass",update_sku_result["output"])
            else:
                return ("Fail",update_sku_result["msg"])
        except:
            return "货柜上下货失败"
    def config_store_threshold(self,dev_id,union_id,barcode,pos_id,threshold):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "union_id": str(union_id),
                    "command": "update_dev_sku", "barcode": str(barcode), "dev_id": str(dev_id), "pos": str(pos_id),
                    "reserve_thr": str(threshold), "memo": "更新库存阈值"}
            store_threshold_result=self.commit_post(self.url_post_common,postData)
            if store_threshold_result["msg"].lower()=="success":
                return ("Pass",store_threshold_result["msg"])
            else:
                return ("Fail",store_threshold_result["msg"])
        except:
            return "配置库存阀值失败"
    def update_price_box(self,dev_id,union_id,barcode,pos_id,price):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "union_id": str(union_id),
                        "command": "update_dev_sku_price", "barcode": str(barcode), "dev_id": str(dev_id),
                        "pos": str(pos_id), "price": str(price), "memo": "update dev sku price"}
            update_price_result=self.commit_post(self.url_post_common,postData)
            if update_price_result["msg"].lower()=="success":
                return ("Pass",update_price_result["msg"])
            else:
                return ("Fail",update_price_result["msg"])
        except:
            return "配置商品价格失败"
    def update_goods_mp3(self,union_id,barcode):
        try:
            name="choose_"+str(barcode)+".mp3"
            postData={"access_token": self.token, "jwtauth_auth_ret_type": "json", "dev_uid": str(union_id),"command": "UpdateDevSkuVoice", "name": name}
            update_mp3_rsult=self.commit_post(self.url_box_mgmt,postData)
            if update_mp3_rsult["msg"].lower()=="success":
                return ("Pass",update_mp3_rsult["msg"])
            else:
                return ("Fail",update_mp3_rsult["msg"])
        except:
            return "更新商品语音失败"
    def sync_config_box(self,dev_id):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "dev_id": str(dev_id),"command": "FullSyncDevSku"}
            sync_result=self.commit_post(self.url_box_mgmt,postData)
            if sync_result["msg"].lower()=="success":
                return ("Pass",sync_result["output"])
            else:
                return ("Fail",sync_result["msg"])
        except:
            return "商品同步失败"
    def clear_config_box(self,dev_id,union_id):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "dev_id": str(dev_id),"union_id": str(union_id), "command": "FullSyncSku", "check_level": 1,
                        "sku_list": []}
            clear_result=self.commit_post(self.url_box_mgmt,postData)
            if clear_result["msg"].lower()=="success":
                return ("Pass",clear_result["output"])
            else:
                return ("Fail",clear_result["msg"])
        except:
            return "清除商品配置失败"
    def check_sku_impact(self,dev_id):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "dev_id": str(dev_id),
                        "command": "query_sku_check_info", "check_level": 1}
            check_impact_result=self.commit_post(self.url_post_common,postData)
            if check_impact_result["msg"].lower()=="success":
                return ("Pass",check_impact_result["output"])
            else:
                return ("Fail",check_impact_result["msg"])
        except:
            return "商品检测同步失败"
    def apply_template_to_box(self,dev_id,union_id,*sku_list):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "dev_id": str(dev_id),
                        "command": "FullSyncSku", "check_level":1,"sku_list":sku_list,"union_id":union_id}
            apply_template_result=self.commit_post(self.url_box_mgmt,postData)
            if apply_template_result["msg"].lower()=="success":
                return ("Pass",apply_template_result["output"])
            else:
                return ("Fail",apply_template_result["msg"])
        except:
            return "同步模板失败"
    def query_templates_all(self):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_dev_profile"}
            query_templates_result=self.commit_post(self.url_post_common,postData)
            if query_templates_result["msg"].lower()=="success":
                return ("Pass",query_templates_result["output"])
            else:
                return ("Fail",query_templates_result["msg"])
        except:
            return "查询模板失败"
    def query_template_detail(self,template_name):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_dev_profile_sku",
                        "profile_name": str(template_name)}
            template_detail_result=self.commit_post(self.url_post_common,postData)
            if template_detail_result["msg"].lower()=="success":
                return ("Pass",template_detail_result["output"])
            else:
                return ("Fail",template_detail_result["msg"])
        except:
            return "模板配置查询失败"
    def add_delete_template(self,**args):
        #box_model设备类型，profile_dev_type货柜类型，weigh_type称台类型
        #"command":"add_dev_profile","profile_dev_type":str(profile_dev_type),"box_model":str(box_model),"profile_name":str(profile_name),"weigh_type":str(weigh_type)
        #"command":"del_dev_profile","profile_name":str(profile_name),
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json",}
            for key,value in args.items():
                postData[key]=value
            operation_template_result=self.commit_post(self.url_post_common,postData)
            if operation_template_result["msg"].lower()=="success":
                return ("Pass",operation_template_result["msg"])
            else:
                return ("Fail",operation_template_result["msg"])
        except:
            return "创建删除模板失败"
    def add_delete_sku_template(self,command_type,pos_id,barcode,operation,profile_name):
        #command:"add_dev_sku"，"update_dev_sku"
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "dev_id": "0", "union_id": "0",
                        "command": str(command_type), "pos": str(pos_id), "check_level": 1, "barcode": str(barcode),
                        "operation": int(operation), "profile_cfg": True, "profile_name": str(profile_name)}
            config_sku_result=self.commit_post(self.url_post_common,postData)
            if config_sku_result["msg"].lower()=="success":
                return ("Pass",config_sku_result["msg"])
            else:
                return ("Fail",config_sku_result["msg"])
        except:
            return "模板添加商品失败"
    def config_weigh_tryp(self,dev_id,weigh_type):
        try:
            postData={"access_token":self.token,"jwtauth_auth_ret_type":"json","command":"update_dev_weigh_type","dev_id":int(dev_id),"weigh_type":int(weigh_type)}
            config_weigh_type_result=self.commit_post(self.url_weigh_type,postData)
            if config_weigh_type_result["msg"].lower()=="success":
                return ("Pass",config_weigh_type_result["output"])
            else:
                return ("Fail",config_weigh_type_result["msg"])
        except:
            return ("Fail","配置货柜类型失败")
    def config_project_info(self,dev_id):
        try:
            postData={"access_token":self.token,"jwtauth_auth_ret_type":"json","command":"update_or_bind_dev_project","dev_id":int(dev_id),"project_info":{"name":"auto_test","company_name":"ustar","city_name":"杭州","addr":"滨江","longitude":"100","latitude":"100","province_name":"浙江","district_code":"滨江"}}
            config_project_info=self.commit_post(self.url_post_common,postData)
            if config_project_info["msg"].lower()=="success":
                return ("Pass",config_project_info["output"])
            else:
                return ("Fail",config_project_info["msg"])
        except:
            return ("Fail","配置项目信息失败")
    def query_project_info(self,dev_id):
        try:
            postData={"access_token":self.token,"jwtauth_auth_ret_type":"json","command":"query_dev_project","dev_id":int(dev_id)}
            query_project_info=self.commit_post(self.url_post_common,postData)
            if query_project_info["msg"].lower()=="success":
                return ("Pass",query_project_info["output"])
            else:
                return ("Fail",query_project_info["msg"])
        except:
            return ("Fail","查询项目信息失败")
    def query_dev_info(self):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "query_dev_info"}
            query_dev_info_status = self.commit_post(self.url_post_common, postData)
            if query_dev_info_status["msg"].lower() == "success":
                return ("Pass", query_dev_info_status["output"])
            else:
                return ("Fail", query_dev_info_status["msg"])
        except:
            return ("Fail", "查询设备信息失败")
    def query_alarm_info(self):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json", "command": "QueryAlmInfo","language": "ch"}
            query_alarm_info = self.commit_post(self.url_alarm, postData)
            if query_alarm_info["msg"].lower() == "success":
                return ("Pass", query_alarm_info["output"]["alm_info_list"])
            else:
                return ("Fail", query_alarm_info["msg"])
        except:
            return ("Fail", "查询告警信息失败")
    def query_alarm(self,**args):
        #command QueryCurAlm,QueryHisAlm;alm_level_list: [0, 1, 2, 3];dev_list[1,2,3];alm_list: [100]
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json"}
            for key,value in args.items():
                postData[key]=value
            query_cur_alarm_info=self.commit_post(self.url_alarm,postData)
            if query_cur_alarm_info["msg"].lower()=="success":
                return ("Pass",query_cur_alarm_info["output"]["alm_list"])
            else:
                return ("Fail",query_cur_alarm_info["msg"])
        except:
            return "查询告警上报信息失败"
    def query_alarm_sub(self,**args):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json","command": "QueryAlmSub"}
            for key,value in args.items():
                postData[key]=value
            query_alarm_sub_info=self.commit_post(self.url_alarm,postData)
            if query_alarm_sub_info["msg"].lower()=="success":
                return ("Pass",query_alarm_sub_info["output"])
            else:
                return ("Fail",query_alarm_sub_info["msg"])
        except:
            return "查询告警订阅信息失败"
    def add_alarm_sub(self,dev_list,alarm_list):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json","command": "AddAlmSub","alm_evt_id_list":alarm_list,"dev_list":dev_list,"notify_way": 1}
            add_alarm_sub_info=self.commit_post(self.url_alarm,postData)
            if add_alarm_sub_info["msg"].lower()=="success":
                return ("Pass",add_alarm_sub_info["output"])
            else:
                return ("Fail",add_alarm_sub_info["msg"])
        except:
            return "告警订阅提交失败"
    def del_alarm_sub(self,*del_list):
        try:
            postData = {"access_token": self.token, "jwtauth_auth_ret_type": "json","command": "DelAlmSub","del_list":del_list}
            del_alarm_sub_info=self.commit_post(self.url_alarm,postData)
            if del_alarm_sub_info["msg"].lower()=="success":
                return ("Pass",del_alarm_sub_info["output"])
            else:
                return ("Fail",del_alarm_sub_info["msg"])
        except:
            return "取消告警订阅失败"

    def alarm_sub_test(dev_list):
        # 订阅告警
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_data = {"dev_list": dev_list}
        rel, query_alarm_sub_info = self.mERP.query_alarm_sub(**query_data)
        alarm_sub_init = False
        if rel == "Pass":
            if query_alarm_sub_info:
                for i in range(len(query_alarm_sub_info)):
                    query_alarm_sub_info[i].pop("notify_way")
                rel, sub_alarm_del = self.mERP.del_alarm_sub(*query_alarm_sub_info)
                if rel == "Pass":
                    alarm_sub_init = True
                else:
                    tip = "初始化删除告警订阅失败" + str(sub_alarm_del)
                    self.save_log.write_case("0", "alarm_sub", "Fail", tip, case_tm)
                    return
            else:
                alarm_sub_init = True
        else:
            tip = "初始查询订阅信息失败" + str(query_alarm_sub_info)
            self.save_log.write_case("0", "alarm_sub", "Fail", tip, case_tm)
            return
        if alarm_sub_init:
            add_alarm_type = [107, 108, 113, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 302, 101, 102, 103, 104,
                              105, 106, 109, 110, 111, 112, 100]
            rel, add_alarm_sub_info = self.mERP.add_alarm_sub(dev_list, add_alarm_type)
            if rel == "Pass":
                self.save_log.write_case("0", "alarm_sub", "Pass", "Pass", case_tm)
            else:
                self.save_log.write_case("0", "alarm_sub", "Fail", add_alarm_sub_info, case_tm)
                return
        time.sleep(5)
        # 查询告警订阅
        case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        query_data = {"dev_list": dev_list}
        rel, query_alarm_sub_status = self.mERP.query_alarm_sub(**query_data)
        if rel == "Pass":
            if query_alarm_sub_status:
                if len(query_alarm_sub_status) == len(add_alarm_type):
                    add_alarm_type.sort()
                    query_alarm_sub_type = []
                    for i in range(len(query_alarm_sub_status)):
                        query_alarm_sub_type.append(query_alarm_sub_status[i]["alm_evt_id"])
                    query_alarm_sub_type.sort()
                    if add_alarm_type == query_alarm_sub_type:
                        self.save_log.write_case("0", "add_larm_sub", "Pass", "Pass", case_tm)
                    else:
                        tip = "查询和订阅不一致" + str(query_alarm_sub_status)
                        self.save_log.write_case("0", "add_alarm_sub", "Fail", tip, case_tm)
                else:
                    tip = "查询和订阅不个数一致" + str(query_alarm_sub_status)
                    self.save_log.write_case("0", "add_alarm_sub", "Fail", tip, case_tm)
            else:
                self.save_log.write_case("0", "add_alarm_sub", "Fail", query_alarm_sub_status, case_tm)
        else:
            self.save_log.write_case("0", "add_alarm_sub", "Fail", query_alarm_sub_status, case_tm)
















