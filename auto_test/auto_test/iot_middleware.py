import json
import re
import time
import requests

class iot_api():
    def __init__(self,web_url,dev_uid):
        self.dev_id=dev_uid
        self.web_url=web_url
    def open_door(self,trans_id):
        url=self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": { \"A\": 51,\"P\": {\"lockid\": \"1-1-1\",\"transid\": \""+str(trans_id)+"\" } }}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        open_door_org=json.loads(response.text)
        if open_door_org["msg"].lower()=="success":
            return "Pass",None
        else:
            return "Fail",open_door_org["msg"]
    def query_door_status(self):
        url=self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": { \"A\": 52,\"P\": {\"lockid\": \"1-1-1\" } }}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        door_status_org = json.loads(response.text)
        if door_status_org["msg"].lower()=="success":
            return "Pass",door_status_org["output"]
        else:
            return "Fail",door_status_org["msg"]
    def set_door_locknumber(self,number):
        url=self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": { \"A\": 55,\"P\": {\"lockid\": \"1-1-1\",\"locknumber\":"+str(number)+"}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        set_status_org = json.loads(response.text)
        if set_status_org["msg"].lower()=="success":
            return "Pass",None
        else:
            return "Fail",set_status_org["msg"]
    def set_door_open_time(self,open_time):
        url=self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": { \"A\": 53,\"P\": {\"lockid\": \"1-1-1\",\"opentime\":"+str(open_time)+"}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        open_time_org = json.loads(response.text)
        print(open_time_org)
        if open_time_org["msg"].lower()=="success":
            return "Pass",None
        else:
            return "Fail",open_time_org["msg"]
    def query_volume(self):
        url=self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": { \"A\": 302}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        volume_org = json.loads(response.text)
        if volume_org["msg"].lower()=="success":
            return "Pass",volume_org["output"]["volume"]
        else:
            return "Fail",volume_org["msg"]
    def set_volume(self,set_volume):
        url=self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": { \"A\": 301,\"P\":{\"soundinfo\":{\"volume\":\""+str(set_volume)+"\"}}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        set_volume_org = json.loads(response.text)
        if set_volume_org["msg"].lower()=="success":
            return "Pass",None
        else:
            return "Fail",set_volume_org["msg"]
    def update_mp3(self,file_name):
        url=self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 304,\"P\":{\"fname\":\""+str(file_name)+"\"}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        update_mp3_org = json.loads(response.text)
        if update_mp3_org["msg"].lower()=="success":
            return "Pass",None
        else:
            return "Fail",update_mp3_org["msg"]
    def manual_play_welcom(self,type):
        url=self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 303,\"P\": {\"event_type\":"+str(type)+"}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        manual_paly_org = json.loads(response.text)
        if manual_paly_org["msg"].lower()=="success" or manual_paly_org["msg"].lower()=="IOT_CLIENT_RETURN_NO_CONTENT":
            return "Pass",None
        else:
            return "Fail",manual_paly_org["msg"]
    def manual_play_channel(self,channel_id):
        url=self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 303,\"P\": {\"event_type\":3,\"goods_id\":[\""+str(channel_id)+"\"]}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        manual_paly_channel_org = json.loads(response.text)
        if manual_paly_channel_org["msg"].lower()=="success" or manual_paly_channel_org["msg"].lower()=="IOT_CLIENT_RETURN_NO_CONTENT":
            return "Pass",None
        else:
            return "Fail",manual_paly_channel_org["msg"]
    def query_csq(self):
        url=self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 351}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        query_csq_org = json.loads(response.text)
        if query_csq_org["msg"].lower()=="success":
            csq_org=query_csq_org["output"]["outputret"]
            print(csq_org)
            csq=re.findall("(\d+),\d",csq_org)
            return "Pass",csq[0]
        else:
            return "Fail",query_csq_org["msg"]
    def query_ccid(self):
        url=self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 353}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        query_ccid_org = json.loads(response.text)
        if query_ccid_org["msg"].lower()=="success":
            ccid_org=query_ccid_org["output"]["outputret"]
            ccid=re.findall("(\d+\S+)",ccid_org)
            return "Pass",ccid[0]
        else:
            return "Fail",query_ccid_org["msg"]
    def query_creg(self):
        url=self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 352}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        query_creg_org = json.loads(response.text)
        if query_creg_org["msg"].lower()=="success":
            creg_org=query_creg_org["output"]["outputret"]
            creg=re.findall("(\d+)",creg_org)
            return "Pass",creg
        else:
            return "Fail",query_ccid_org
    def weigh_adjust(self,layer,adj_value):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 103,\"P\": {\"weighadjustinfo\":[{\"adjust\": true,\"weighid\": \""+str(layer)+"\",\"actualweight\":"+str(adj_value)+"}]}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        weigh_adjust_org = json.loads(response.text)
        if weigh_adjust_org["msg"].lower()=="success":
            return "Pass",None
        else:
            return "Fail",weigh_adjust_org["msg"]
    def query_adjust(self):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 104}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        query_weigh_adjust_org = json.loads(response.text)
        if query_weigh_adjust_org["msg"].lower() == "success":
            return "Pass",query_weigh_adjust_org["output"]
        else:
            return "Fail",query_weigh_adjust_org["msg"]
    def clear_weight(self,layer):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 105,\"P\": {\"weighclearinfo\":[{\"clear\": true,\"weighid\": \""+str(layer)+"\"}]}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        clear_weight_org = json.loads(response.text)
        if clear_weight_org["msg"].lower()=="success":
            return "Pass",None
        else:
            return "Fail",clear_weight_org["msg"]
    def query_clear_weight(self):
        url = self.web_url
        payload = "{\"devname\": \"1012018102200537\",\"req\": {\"A\": 106}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        query_clear_weight_org = json.loads(response.text)
        if query_clear_weight_org["msg"].lower()=="success":
            return "Pass",query_clear_weight_org["output"]
        else:
            return "Fail",query_clear_weight_org["msg"]

    def query_weigh_algorithmattr(self):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 119}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        query_weigh_algorithmattr_org = json.loads(response.text)
        if query_weigh_algorithmattr_org["msg"].lower()=="success":
            return "Pass",query_weigh_algorithmattr_org["output"]["attr"]
        else:
            return "Fail",query_weigh_algorithmattr_org["msg"]
    def set_weigh_algorithmattr(self,attr_value):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 118,\"P\":{\"algorithmattr\":{ \"attr\":"+str(attr_value)+"}}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        set_weigh_algorithmattr_org = json.loads(response.text)
        if set_weigh_algorithmattr_org["msg"].lower()=="success":
            return "Pass",None
        else:
            return "Fail",set_weigh_algorithmattr_org["msg"]
    def query_all_weight(self):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 107,\"P\":{}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        query_weight_org = json.loads(response.text)
        if query_weight_org["msg"].lower()=="success":
            return "Pass",query_weight_org["output"]
        else:
            return "Fail",query_weight_org["msg"]

    def query_single_weight(self,layer):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 107,\"P\":{\"wId\": \""+str(layer)+"\"}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        query_weight_org = json.loads(response.text)
        if query_weight_org["msg"].lower()=="success":
            return "Pass",query_weight_org["output"]
        else:
            return "Fail",query_weight_org["msg"]
    def query_goods_num(self,layer):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 109,\"P\": {}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        query_goods_num_org = json.loads(response.text)
        if query_goods_num_org["msg"].lower()=="success":
            for i in range(len(query_goods_num_org["output"])):
                if query_goods_num_org["output"][i]["weighid"]==str(layer):
                    return "Pass",query_goods_num_org["output"][i]["goodslist"]
        else:
            return "Fail",query_goods_num_org["msg"]
    def query_weight_online(self):
        url = self.web_url
        payload = "{\"req\":{\"A\":112},\"devname\": \""+ self.dev_id+ "\"}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        query_weight_online_org = json.loads(response.text)
        if query_weight_online_org["msg"].lower()=="success":
            return "Pass",query_weight_online_org["output"]
        else:
            return "Fail",query_weight_online_org["msg"]
    def query_weight_online_single(self,layer):
        url = self.web_url
        payload = "{\"req\":{\"A\":112},\"devname\": \""+ self.dev_id+ "\"}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        query_weight_online_org = json.loads(response.text)
        if query_weight_online_org["msg"].lower()=="success":
            for i in range(len(query_weight_online_org["output"])):
                if query_weight_online_org["output"][i]["weighid"] == str(layer):
                    return "Pass",query_weight_online_org["output"][i]["online"]
        else:
            return "Fail",query_weight_online_org["msg"]
    def add_commodity(self,layer,goods_id,weight_min,weight_max,goods_num):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 113,\"P\": {\"weighcfginfo\":[{\"enable\": true,\"weighid\": \""+str(layer)+"\",\"goodsweightinfo\":[{\"goodsid\": \""+str(goods_id)+"\",\"isstandard\": true,\"weightmin\": "+str(weight_min)+",\"weightmax\": "+str(weight_min)+",\"goodsnum\": "+str(goods_num)+",\"goodsvalue\": 0,\"goodsname\": \"\"}]}]}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        add_commodity_org = json.loads(response.text)
        if add_commodity_org["msg"].lower()=="success":
            return "Pass",None
        else:
            return "Fail",add_commodity_org["msg"]
    def del_commodity(self,layer,goods_id):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 114,\"P\": {\"weighid\": \""+ str(layer)+ "\", \"goodsid\":\""+ sttr(goods_id)+ "\"}}}"
        headers = {'Content-Type': "application/json",'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7" }
        response = requests.request("POST", url, data=payload, headers=headers)
        del_commodity_org = json.loads(response.text)
        if del_commodity_org["msg"].lower()=="success":
            return "Pass",None
        else:
            return "Fail",del_commodity_org["msg"]
    def change_basic_weight(self,layer,goods_id,weight_min,weight_max):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 115,\"P\": {   \"weighcfginfo\":[{\"weighid\": \""+ str(layer)+ "\",\"goodsweightinfo\":[{\"goodsid\": \""+ str(goods_id)+ "\",\"weightmin\": "+ str(weight_min)+ ",\"weightmax\":"+ str(weight_max)+ "}]}]}}}"
        headers = {'Content-Type': "application/json", 'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7"}
        response = requests.request("POST", url, data=payload, headers=headers)
        change_basic_weight_org = json.loads(response.text)
        if change_basic_weight_org["msg"].lower()=="success":
            return "Pass",None
        else:
            return "Fail",change_basic_weight_org["msg"]
    def change_goods_num(self,layer,goods_id,goods_num):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 115,\"P\": {   \"weighcfginfo\":[{\"weighid\": \""+ str(layer)+ "\",\"goodsweightinfo\":[{\"goodsid\": \""+ str(goods_id)+ "\",\"goodsnum\": "+ str(goods_num)+ "}]}]}}}"
        headers = {'Content-Type': "application/json", 'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7"}
        response = requests.request("POST", url, data=payload, headers=headers)
        change_goods_num_org = json.loads(response.text)
        if change_goods_num_org["msg"].lower()=="success":
            return "Pass",None
        else:
            return "Fail",change_goods_num_org["msg"]
    def query_app_version(self):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 151}}"
        headers = {'Content-Type': "application/json", 'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7"}
        response = requests.request("POST", url, data=payload, headers=headers)
        app_version_org = json.loads(response.text)
        if app_version_org["msg"].lower()=="success":
            return "Pass",app_version_org["output"]
        else:
            return "Fail",app_version_org["msg"]
    def stop_app(self,app_name):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 152,\"P\": {\"appname\": \""+str(app_name)+"\",\"action\": 5}}}"
        headers = {'Content-Type': "application/json", 'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7"}
        response = requests.request("POST", url, data=payload, headers=headers)
        app_stop_org = json.loads(response.text)
        if app_stop_org["msg"].lower()=="success":
            return "Pass",app_stop_org["output"]
        else:
            return "Fail",app_stop_org["msg"]
    def query_app_operat_status(self,pid_id):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": { \"A\": 153,\"P\": {\"pid\":\""+str(pid_id)+"\"}}}"
        headers = {'Content-Type': "application/json", 'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7"}
        response = requests.request("POST", url, data=payload, headers=headers)
        app_status_org = json.loads(response.text)
        if app_status_org["msg"].lower()=="success":
            return "Pass",pp_status_org["output"]
        else:
            return "Fail",app_status_org["msg"]
    def start_app(self,app_name,port):
        url = self.web_url
        payload = "{\"devname\": \""+ self.dev_id+ "\",\"req\": {\"A\": 152,\"P\": {\"appname\": \""+str(app_name)+"\",\"action\": 4,\"port\":\""+str(port)+"\"}}}"
        headers = {'Content-Type': "application/json", 'cache-control': "no-cache",'Postman-Token': "1f4c5013-b7de-4404-ad2e-74cfb28aacc7"}
        response = requests.request("POST", url, data=payload, headers=headers)
        app_start_org = json.loads(response.text)
        if app_start_org["msg"].lower()=="success":
            return "Pass",app_start_org["output"]
        else:
            return "Fail",app_start_org["msg"]







