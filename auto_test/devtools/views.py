#-*- coding: UTF-8 -*-#-*- coding: UTF-8 -*-
# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render_to_response,render
from django.template import Context,RequestContext
import urllib
from http import cookiejar
import time
from auto_test.iot_middleware import iot_api
from collections import OrderedDict
import requests
import os.path
import paramiko
from auto_test import celery_app as app
from devtools import tasks
import threading
from django.core.cache import cache
import re
import glob
from .models import down_load_process

def dev_operator(request):
    return render_to_response("dev_operation.html")


@csrf_exempt
def dev_attr(request):
    #display_type_org=request.getParameter("select_attr")
    #display_type=display_type_org.value
    #print(display_type)
    respons_date = {}
    date = json.loads(request.body.decode("utf8"))
    dev_env=int(date["dev_env"])
    dev_id=int(date["dev_id"])
    display_type=int(date["display_type"])
    union_id, online_status = get_dev_status(dev_env, dev_id)
    respons_date_content=[]
    if union_id:
        if online_status == 0:
            respons_date_content.append({'dev_status':"0"})
            respons_date["output"]=respons_date_content
            return HttpResponse(json.dumps(respons_date),content_type="application/json charset=utf-8")
        elif online_status == 1 :
            respons_date_content.append({'dev_status':"1"})
        else:
            respons_date_content.append({'dev_status':online_status})
            respons_date["output"]=respons_date_content
            return HttpResponse(json.dumps(respons_date),content_type="application/json charset=utf-8")
    else:
        respons_date_content.append({'dev_status':online_status})
        respons_date["output"] = respons_date_content
        return HttpResponse(json.dumps(respons_date),content_type="application/json charset=utf-8")
    if display_type==4:
        #sub_respons_date.append({"title_name":[{"csq":"4G信号强度查询"},{"ccid":"CCID查询"}]})
        respons_date_content.append({"title_name":[{"csq":"4G信号强度查询"},{"ccid":"CCID查询"}]})
        respons_date["output"] = respons_date_content
        return HttpResponse(json.dumps(respons_date),content_type="application/json charset=utf-8")
    elif display_type==3:
        #sub_respons_date.append({"title_name":[{"door_status":"门锁状态"},{"lock_time":"落锁时间设置"}]})
        respons_date_content.append({"title_name":[{"door_status":"门锁状态"},{"lock_time":"落锁时间设置"}]})
        respons_date["output"] = respons_date_content
        return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
    elif display_type==2:
        #sub_respons_date.append({"title_name":[{"volume_value":"音量查询"},{"volume_set":"音量设置"}]})
        respons_date_content.append({"title_name":[{"volume_value":"音量查询"},{"volume_set":"音量设置"}]})
        respons_date["output"] = respons_date_content
        return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
    elif display_type==1:
        #sub_respons_date.append({"title_name":[{"weigh_attr_set":"weigh属性配置"},{"weigh_attr_query":"weigh属性查询"},{"weigh_online":"当前重量和在线情况查询"}]})
        respons_date_content.append({"title_name":[{"weigh_attr_set":"weigh属性配置"},{"weigh_attr_query":"weigh属性查询"},{"weigh_online":"当前重量和在线情况查询"}]})
        respons_date["output"] = respons_date_content
        return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")

@csrf_exempt
def ajax_attr_value(request):
    respons_date = {}
    date = json.loads(request.body.decode("utf8"))
    print(date)
    attr_type=int(date["attr_type"])
    dev_env=int(date["dev_env"])
    dev_id=int(date["dev_id"])
    query_id=date["query_id"]
    union_id,online_status=get_dev_status(dev_env,dev_id)
    sub_respons_date=[]
    if dev_env==0:
        api_url="http://10.4.32.114:8085/rrpc"
    elif dev_env==1:
        api_url="http://w.vegcloud.xyz:8085/rrpc"
    opt_api=iot_api(api_url,union_id)
    if attr_type==4:
        if query_id=="csq":
            rel,csq_value=opt_api.query_csq()
            sub_respons_date.append({'csq':csq_value})
        elif query_id =="ccid":
            rel,ccid_value=opt_api.query_ccid()
            sub_respons_date.append({'ccid': ccid_value})
        respons_date["output"] = sub_respons_date
        return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
    elif attr_type==3:
        if query_id=="door_status":
            rel,door_status=opt_api.query_door_status()
            if door_status["locked"]==1:
                sub_respons_date.append({'门锁状态':"关"})
            elif door_status["locked"]==0:
                sub_respons_date.append({'门锁状态': "开"})
            else:
                sub_respons_date.append({'门锁状态': "异常"})
            if door_status["closed"]==1:
                sub_respons_date.append({'门磁状态': "关"})
            elif door_status["closed"]==0:
                sub_respons_date.append({'门磁状态': "开"})
            else:
                sub_respons_date.append({'门锁状态': "异常"})
            respons_date["output"] = sub_respons_date
            return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
        elif query_id=="lock_time":
            open_door_time=date["lock_time"]
            rel,set_lock_status=opt_api.set_door_open_time(open_door_time)
            if rel=="Pass":
                sub_respons_date.append({'落锁时间设置成功': open_door_time})
                respons_date["output"]=sub_respons_date
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
            elif rel=="Fail":
                sub_respons_date.append({'落锁时间设置失败':set_lock_status })
                respons_date["output"]=sub_respons_date
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
    elif attr_type==2:
        if query_id=="volume_value":
            rel,query_value=opt_api.query_volume()
            if rel=="Pass":
                sub_respons_date.append({'当前音量值': query_value})
                respons_date["output"]=sub_respons_date
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
            elif rel=="Fail":
                sub_respons_date.append({'查询音量失败': query_value})
                respons_date["output"]=sub_respons_date
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
        elif query_id=="volume_set":
            volume_value=int(date["volume_value"])
            rel,set_status=opt_api.set_volume(volume_value)
            if rel=="Pass":
                sub_respons_date.append({'音量设置成功': volume_value})
                respons_date["output"]=sub_respons_date
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
            elif rel=="Fail":
                sub_respons_date.append({'音量设置失败':set_status})
                respons_date["output"]=sub_respons_date
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
    elif attr_type==1:
        if query_id=="weigh_attr_query":
            rel,weigh_attr=opt_api.query_weigh_algorithmattr()
            if rel=="Pass":
                sub_respons_date.append({'当前属性值': weigh_attr})
                respons_date["output"]=sub_respons_date
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
            elif rel=="Fail":
                sub_respons_date.append({'当前属性查询失败': weigh_attr})
                respons_date["output"]=sub_respons_date
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
        elif query_id=="weigh_attr_set":
            weigh_attr_value=date["weigh_attr_value"]
            rel,weigh_attr_set_status=opt_api.set_weigh_algorithmattr(weigh_attr_value)
            if rel=="Pass":
                sub_respons_date.append({'设置属性值成功': weigh_attr_value})
                respons_date["output"]=sub_respons_date
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
            elif rel=="Fail":
                sub_respons_date.append({'设置属性值失败': weigh_attr_set_status})
                respons_date["output"]=sub_respons_date
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
        elif query_id=="weigh_online":
            weight_layer=OrderedDict()
            #weight_layer={"010101":"第一层左","010201":"第二层左","010301":"第三层左","010401":"第四层左","010501":"第五层左","010102":"第一层右","weight_layerweight_layer["左一层":010101],"010202":"第二层右","010302":"第三层右","010402":"第四层右","010502":"第五层右",}
            weight_layer["左一层"] = "010101"
            weight_layer["左二层"]="010201"
            weight_layer["左三层"]="010301"
            weight_layer["左四层"]= "010401"
            weight_layer["左五层"]= "010501"
            weight_layer["右一层"]= "010102"
            weight_layer["右二层"]= "010202"
            weight_layer["右三层"]= "010302"
            weight_layer["右四层}"]= "010402"
            weight_layer["右五层"]="010502"
            rel,weight_weight=opt_api.query_all_weight()
            if rel=="Pass":
                for key, value in weight_layer.items():
                    for i in range(len(weight_weight)):
                        if str(weight_weight[i]["weighid"]) == str(value):
                            if weight_weight[i]["weight"] != 0:
                                sub_respons_date.append({key: weight_weight[i]["weight"]})
                respons_date["output"]=sub_respons_date
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
            elif rel=="Fail":
                respons_date["output"]=sub_respons_date
                sub_respons_date.append({'查询秤盘重量': weight_weight})
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")

@csrf_exempt
def order_analyze(request):
    return render_to_response("order_analyze.html")

@csrf_exempt
def get_trans_id(request):
    respons_date = {}
    date = json.loads(request.body.decode("utf8"))
    print(date)
    #global process_size,sum_size
    dev_type=date["type"]
    trans_id=date["trans_id"].strip()
    trans_id=trans_id.replace("\\u200c","")
    dev_id=date["dev_id"]
    operation=date["operation"]
    dev_env=int(date["dev_env"])
    if operation=="get_file":
        file_type=date["file_type"]
        respons_date=operation_process(dev_env, dev_id, trans_id, dev_type, file_type)
        return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
    elif operation=="analyze_operation":
        login_user = date["login_user"]
        login_pw = date["login_pw"]
        if dev_type=="AS":
            open_goods,close_goods,change_goods,actual_change_weight=as_goods_filter(trans_id)
            rel, goods_date_info = get_goods_info(dev_env, login_user, login_pw)
            if rel=="Fail":
                respons_date['down_load_status'] = 'get goods date fail'
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
            elif rel =="Pass":
                change_goods = as_add_goods_weight(change_goods, goods_date_info)
                chg_weight = change_weight(change_goods)
                respons_date['output'] = [{"open_goods":open_goods},{"close_goods":close_goods},{"change_goods":change_goods},{"chg_weight":chg_weight},{"actual_change_weight":actual_change_weight}]
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
        elif dev_type == "CM":
            open_goods,close_goods,change_goods, actual_change_weight,open_image_url_date,close_image_url_date = cm_goods_filter(trans_id)
            rel, goods_date_info = get_goods_info(dev_env, login_user, login_pw)
            if rel=="Fail":
                respons_date['down_load_status'] = 'get goods date fail'
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
            elif rel =="Pass":
                change_goods = cm_add_goods_name_wight(change_goods, goods_date_info)
                chg_weight = change_weight(change_goods)
                open_goods=cm_add_goods_name_wight(open_goods,goods_date_info)
                close_goods=cm_add_goods_name_wight(close_goods,goods_date_info)
                respons_date['output'] = [{"open_goods":open_goods},{"close_goods":close_goods},{"change_goods":change_goods},{"chg_weight":chg_weight},{"actual_change_weight":actual_change_weight},{"open_image_url_date":open_image_url_date},{"close_image_url_date":close_image_url_date}]
                return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")
    if operation=="get_image":
        file_type=date["file_type"]
        respons_date=operation_process(dev_env, dev_id, trans_id, dev_type, file_type)
        return HttpResponse(json.dumps(respons_date), content_type="application/json charset=utf-8")

def operation_process(dev_env,dev_id,trans_id,dev_type,file_type):
    respons_date={}
    base_local_file, base_remote_file = base_path_file(dev_type, file_type)
    if file_type=="log":
        local_file=base_local_file + str(trans_id) + ".txt"
    elif file_type=="image":
        local_file = base_local_file + str(trans_id) + "*"
    elif dev_type=="CM" and file_type=="image":
        local_file=base_local_file+str(trans_id)+".txt"
    log_is_exist = glob.glob(local_file)
    if log_is_exist:
        respons_date['down_load_status'] = "file is exist local"
        if dev_type=="AS" and file_type=="image":
            file_name_tem_sub = []
            for i in range(len(log_is_exist)):
                file_name_tem = log_is_exist[i].replace("/home/stcomm/log/AS/image/", "")
                file_name_tem_sub.append(file_name_tem)
            respons_date["file_list"] = file_name_tem_sub
        elif  dev_type=="CM" and file_type=="image":
            respons_date['down_load_status'] = "cm image file is exist local"
            _, _, _, _, open_image_url_date, close_image_url_date = cm_goods_filter(trans_id)
            respons_date["file_list"]=[open_image_url_date,close_image_url_date]
        return respons_date
    else:
        union_id, online_status = get_dev_status(dev_env, dev_id)
        frp_status = get_app_status(dev_env, union_id, "frp-client-ssh")
        if frp_status == "stopped":
            rel, open_frp_status = open_frp(env, dev_id, union_id)
            if rel == "Fail":
                respons_date['down_load_status'] = open_frp_status
                return respons_date
        else:
            get_file_status, file_date = get_remote_file(dev_id, dev_type, trans_id, file_type)
            if get_file_status == "Pass":
                total_file_size = file_date["total_file_size"]
                file_name = file_date["file_name"]
                cache.set('process_size', 0, )
                cache.set('sum_size', total_file_size)
                cache.set("counter_size",0)
                if file_name:
                    connect_status, myclient = creat_connect(dev_id)
                    if connect_status == "Fail":
                        respons_date['down_load_status'] = myclient
                        return respons_date
                    elif connect_status == "Pass":
                        down_load_t = threading.Thread(target=down_load_file, args=(myclient, base_remote_file, base_local_file, file_name,))
                        down_load_t.start()
                        respons_date['down_load_status'] = "success"
                        respons_date["file_list"]=file_name
                        return respons_date
                else:
                    respons_date['down_load_status'] = 'remote file is not exist'
                    return respons_date

            elif get_file_status == "Fail":
                respons_date['down_load_status'] = 'Get remote file failure'
                return respons_date

#log和image下载
def base_path_file(dev_type,file_type):
    if file_type=="log":
        if dev_type == "AS":
            local_file = "/home/stcomm/log/AS/"
            remote_file = '/vbg/root/weighcv-as/log/'
        elif dev_type == "CM":
            local_file = "/home/stcomm/log/CM/"
            remote_file = '/vbg/root/weighcv-cm/log/'
    elif file_type=="image":
        if dev_type == "AS":
            local_file = "/home/stcomm/log/AS/image/"
            remote_file = '/vbg/root/weighcv-as/image/'
        elif dev_type == "CM":
            local_file = "/home/stcomm/log/CM/"
            remote_file = '/vbg/root/weighcv-cm/log/'
    return local_file,remote_file
def creat_connect(dev_id):
    ssh_repeat = 0
    if len(str(dev_id)) == 5:
        port_id = int(dev_id)
    else:
        port_id = "2" + str(dev_id)
    hostid = "m.vegcloud.tech"
    sshid = int(port_id)
    name = "linaro"
    pwd = "Ustaff201"
    while True:
        try:
            myclient = paramiko.Transport((hostid, sshid))
            # myclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            myclient.connect(username=name, password=pwd)
            return "Pass",myclient
        except:
            ssh_repeat += 1
            if ssh_repeat > 5:
                return "Fail",None
            time.sleep(10)
def get_remote_file(dev_id,dev_type,trans_id,file_type):
    try:
        hostid = "m.vegcloud.tech"
        if len(str(dev_id)) == 5:
            portid = dev_id
        else:
            portid = "2" + str(dev_id)
        sshid = int(portid)
        name = "linaro"
        pwd = "Ustaff201"
        myclient = paramiko.SSHClient()
        myclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        myclient.connect(hostid, port=sshid, username=name, password=pwd, allow_agent=False, look_for_keys=False)
        if dev_type == "AS":
            if file_type=="image":
                cmd = "ls -l " + "/vbg/root/weighcv-as/image/" + trans_id + "*"
                re_comp=re.compile("root root\s+(\d+).+/vbg/root/weighcv-as/image/(.+)")
            elif file_type=="log":
                cmd= "ls -l "+"/vbg/root/weighcv-as/log/"+trans_id+".txt"
                re_comp = re.compile("root root\s+(\d+).+/vbg/root/weighcv-as/log/(.+)")
        elif dev_type=="CM":
            cmd = "ls -l " + "/vbg/root/weighcv-cm/log/" + trans_id + ".txt"
            re_comp = re.compile("root root\s+(\d+).+/vbg/root/weighcv-cm/log/(.+)")
        stdin, stdout, stderr = myclient.exec_command(cmd)
        file_list = []
        total_file_size=0
        while True:
            find_file_org = stdout.readline()
            if find_file_org:
                file_org = re_comp.findall( find_file_org)
                file_size=file_org[0][0]
                file_name=file_org[0][1]
                total_file_size+=int(file_size)
                file_list.append(file_name)
            else:
                break
        myclient.close()
        return "Pass",{"total_file_size":total_file_size,"file_name":file_list}
    except BaseException as e:
        return "Fail",e
def down_load_file(connect_client,base_remote_file,base_local_file,file_list):
    sftp = paramiko.SFTPClient.from_transport(connect_client)
    def file_size_update(x_now_size, y_total_size):
        counter_size = int(cache.get("counter_size"))
        process_size = counter_size + int(x_now_size)
        cache.set('process_size', process_size, 10)
    for i in range(len(file_list)):
        remote_file=base_remote_file+file_list[i]
        local_file=base_local_file+file_list[i]
        getfile = sftp.get(remote_file, local_file,callback=file_size_update)
        cache.set("counter_size",cache.get("process_size"),10)
    connect_client.close()









#日志过滤
def as_goods_filter(trans_id):
    file_path="/home/stcomm/log/AS/"+trans_id+".txt"
    f = open(file_path, "r", encoding='UTF-8')
    open_date = {}
    open_goods_date = []
    close_date = {}
    close_goods_date = []
    change_date = {}
    detect_close_door = False
    actual_change_weight={}
    while True:
        line = f.readline()
        if line:
            if not detect_close_door:
                detect_close_door = re.findall("ASGetLockChgDetectGoods:", line)
                rel_open = re.compile("DoObjDetect OpenObjDetectInfo weId: \d+ detectinfo=\s+(.+)")
                rel_close = re.compile("DoObjDetect CloseObjDetectInfo weId: \d+ detectinfo=\s(.+)")
                open_detect_org = rel_open.findall(line)
                close_detect_org = rel_close.findall(line)
                if open_detect_org:
                    open_goods_date=[]
                    open_detect_dict = json.loads(open_detect_org[0])
                    open_goods_info_org = open_detect_dict["goodsinfo"]
                    for i in range(len(open_goods_info_org)):
                        open_goods_date_sub = {}
                        open_goods_date_sub["goodsname"] = open_goods_info_org[i]["goodsname"]
                        open_goods_date_sub["goodsnum"] = open_goods_info_org[i]["goodsnum"]
                        open_goods_date.append(open_goods_date_sub)
                    open_date[open_detect_dict["weighid"]] = open_goods_date
                if close_detect_org:
                    close_goods_date = []
                    close_detect_dict = json.loads(close_detect_org[0])
                    close_goods_info_org = close_detect_dict["goodsinfo"]
                    for i in range(len(close_goods_info_org)):
                        close_goods_date_sub = {}
                        close_goods_date_sub["goodsname"] = close_goods_info_org[i]["goodsname"]
                        close_goods_date_sub["goodsnum"] = close_goods_info_org[i]["goodsnum"]
                        close_goods_date.append(close_goods_date_sub)
                    close_date[close_detect_dict["weighid"]] = close_goods_date
                elif detect_close_door:
                    detect_close_door = True
            elif detect_close_door:
                rel_change = re.compile("ChgObjDetect\\[ \d+ \\]=  {\d+ (\d+) 0 \\[(.*?)\\]")
                rel_change_weight = re.compile("DealLockEvent  isclose= true ;weighid=\s+(\d+).+opendiff=\s+(\S+)")
                actual_change_weight_org = rel_change_weight.findall(line)
                change_detect_org = rel_change.findall(line)
                if change_detect_org:
                    is_detect = False
                    change_detect_dict = change_detect_org[0]
                    if change_date:
                        for key, value in change_date.items():
                            if key == change_detect_dict[0]:
                                is_detect = True
                                break
                    if not is_detect:
                        if change_detect_dict[1]:
                            rel_change_goods_filter = re.compile("\{\d+\s+(\d+)\s+(\S+)\s+(\d+)\s+(\d+)?\}?")
                            change_goods_org = rel_change_goods_filter.findall(change_detect_dict[1])
                            change_date_sub = []
                            for i in range(len(change_goods_org)):
                                change_goods_sub = {}
                                change_goods_sub["goodscode"] = change_goods_org[i][0]
                                change_goods_sub["goodsname"] = change_goods_org[i][1]
                                change_goods_sub["goodsnum"] = change_goods_org[i][2]
                                change_goods_sub["change_type"] = change_goods_org[i][3]
                                change_date_sub.append(change_goods_sub)
                            change_date[change_detect_dict[0]] = change_date_sub
                        else:
                            change_date[change_detect_dict[0]] = ""
                elif actual_change_weight_org:
                    actual_change_weight[actual_change_weight_org[0][0]] = actual_change_weight_org[0][1]
        else:
            break
    return open_date,close_date,change_date,actual_change_weight
def cm_goods_filter(trans_id):
    file_path="/home/stcomm/log/CM/"+trans_id+".txt"
    f = open(file_path, "r", encoding='UTF-8')
    open_date = {}
    open_goods_date = []
    close_date = {}
    close_goods_date = []
    open_image_url_date = {}
    close_image_url_date = {}
    change_date = {}
    actual_change_weight={}
    while True:
        line = f.readline()
        if line:
            rel_open = re.compile("CVOpenDoorDo OpenObjDetectInfo detectinfo=\s+(.+)")
            rel_close = re.compile("CVCloseDoorDo CloseObjDetectInfo detectinfo=\s+(.+)")
            rel_change = re.compile("LockChgDetect\\[ \d+ \\]=  {\d+ (\d+) 0 \\[(.*?)\\]")
            rel_change_weight=re.compile("DealLockEvent  isclose= true ;weighid=\s+(\d+).+opendiff=\s+(\S+)")
            open_detect_org = rel_open.findall(line)
            close_detect_org = rel_close.findall(line)
            change_detect_org = rel_change.findall(line)
            actual_change_weight_org=rel_change_weight.findall(line)
            if open_detect_org:
                open_detect_dict = json.loads(open_detect_org[0])
                for i in range(len(open_detect_dict)):
                    open_goods_date=[]
                    open_goods_info_org = open_detect_dict[i]["goodsinfo"]
                    for j in range(len(open_goods_info_org)):
                        open_goods_date_sub = {}
                        open_goods_date_sub["goodscode"] = open_goods_info_org[j]["goodsid"]
                        open_goods_date_sub["goodsnum"] = open_goods_info_org[j]["goodsnum"]
                        open_goods_date.append(open_goods_date_sub)
                    open_date[open_detect_dict[i]["weighid"]] = open_goods_date
                    open_image_url_date[open_detect_dict[i]["weighid"]]=open_detect_dict[i]["imageurl"]
            elif close_detect_org:
                close_detect_dict = json.loads(close_detect_org[0])
                for i in range(len(close_detect_dict)):
                    close_goods_date=[]
                    close_goods_info_org = close_detect_dict[i]["goodsinfo"]
                    for j in range(len(close_goods_info_org)):
                        close_goods_date_sub = {}
                        close_goods_date_sub["goodscode"] = close_goods_info_org[j]["goodsid"]
                        close_goods_date_sub["goodsnum"] = close_goods_info_org[j]["goodsnum"]
                        close_goods_date.append(close_goods_date_sub)
                    close_date[close_detect_dict[i]["weighid"]] = close_goods_date
                    close_image_url_date[close_detect_dict[i]["weighid"]] = close_detect_dict[i]["imageurl"]
            elif change_detect_org:
                is_detect = False
                change_detect_dict = change_detect_org[0]
                if change_date:
                    for key, value in change_date.items():
                        if key == change_detect_dict[0]:
                            is_detect = True
                            break
                if not is_detect:
                    if change_detect_dict[1]:
                        rel_change_goods_filter = re.compile("\{[\-|\+]\d+\s+(\d+)\s+(\d+)\s+(\d+)?\}?")
                        change_goods_org = rel_change_goods_filter.findall(change_detect_dict[1])
                        change_date_sub = []
                        all_zero = True
                        for i in range(len(change_goods_org)):
                            if int(change_goods_org[i][1])!=0:
                                all_zero=False
                                change_goods_sub = {}
                                change_goods_sub["goodscode"] = change_goods_org[i][0]
                                change_goods_sub["goodsnum"] = change_goods_org[i][1]
                                change_goods_sub["change_type"] = change_goods_org[i][2]
                                change_date_sub.append(change_goods_sub)
                                change_date[change_detect_dict[0]] = change_date_sub
                        if all_zero:
                            change_date[change_detect_dict[0]] = ""
                    else:
                        change_date[change_detect_dict[0]] = ""
            elif actual_change_weight_org:
                actual_change_weight[actual_change_weight_org[0][0]]=actual_change_weight_org[0][1]
        else:
            break
    return open_date, close_date, change_date,actual_change_weight,open_image_url_date,close_image_url_date
def get_goods_info(env,erp_user,erp_pw):
    if env==0:
        web_login_url = "http://10.4.32.114:8080/login"
        web_query_goods_url = "http://10.4.32.114:8080/post_common_admin/"
        web_login_Referer = "http://10.4.32.114:8080/g/utstarcom"
        web_query_goods_Referer = "http://10.4.32.114:8080/main"
    elif env==1:
        web_login_url = "https://gosmart.ustar-ai.com/login"
        web_query_goods_url = "https://gosmart.ustar-ai.com/post_common_admin/"
        web_query_goods_Referer = "https://gosmart.ustar-ai.com"
        web_login_Referer = "https://gosmart.ustar-ai.com/g/utstarcom"
    cj = cookiejar.CookieJar()
    cookie_support = urllib.request.HTTPCookieProcessor(cj)
    opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)

    login_url = web_login_url
    headers_login = {'Referer': web_login_Referer,
                     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    postData_login = {'employee_id': erp_user, 'employee_pass': erp_pw}
    postData_login = urllib.parse.urlencode(postData_login, encoding='gb2312').encode('gb2312')
    request_login = urllib.request.Request(login_url, postData_login, headers_login)
    response_login = urllib.request.urlopen(request_login)
    login_text_org = response_login.read().decode()
    login_text = json.loads(login_text_org)
    login_token = login_text["token"]
    query_goods_url = web_query_goods_url
    headers_query_goods = {'Referer': web_query_goods_Referer,
                           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    postData_headers_query = {"access_token": login_token, "jwtauth_auth_ret_type": "json",
                              "command": "query_sku"}

    postData_headers_query = urllib.parse.urlencode(postData_headers_query, encoding='gb2312').encode(
        'gb2312')
    request_query_goods = urllib.request.Request(query_goods_url, postData_headers_query,
                                                 headers_query_goods)
    response_query_goods = urllib.request.urlopen(request_query_goods)
    query_goods_text_org = response_query_goods.read().decode()
    query_goods_text = json.loads(query_goods_text_org)
    if query_goods_text["msg"].lower() == "success":
        return   "Pass",query_goods_text["output"]
    else:
        return "Fail",query_goods_text["msg"]
def cm_add_goods_name_wight(change_goods_date,goods_date_info):
    for key,value in change_goods_date.items():
        for i in range(len(value)):
            for j in range(len(goods_date_info)):
                if goods_date_info[j]["barcode"]==value[i]["goodscode"]:
                    value[i]["goodsname"]=goods_date_info[j]["name"]
                    value[i]["weight_base"] = goods_date_info[j]["weight"]
                    value[i]["weight_drift"]=goods_date_info[j]["weight_drift"]
                    break
    return change_goods_date
def as_add_goods_weight(change_goods_date,goods_date_info):
    for key,value in change_goods_date.items():
        for i in range(len(value)):
            for j in range(len(goods_date_info)):
                if goods_date_info[j]["barcode"]==value[i]["goodscode"]:
                    value[i]["weight_base"] = goods_date_info[j]["weight"]
                    value[i]["weight_drift"] = goods_date_info[j]["weight_drift"]
                    break
    return change_goods_date
def change_weight(change_goods_date):
    change_weight = {}
    for key,value in change_goods_date.items():
        if value:
            change_weight_min = 0
            change_weight_max = 0
            for i in range(len(value)):
                if value[i]["change_type"]== "2":
                    goods_weight_min = int(value[i]["goodsnum"]) * (value[i]["weight_base"] - value[i]["weight_drift"]-5)
                    goods_weight_max = int(value[i]["goodsnum"]) * (value[i]["weight_base"] + value[i]["weight_drift"]+5)
                elif value[i]["change_type"]== "4":
                    goods_weight_min = -int(value[i]["goodsnum"]) * (value[i]["weight_base"] + value[i]["weight_drift"]+5)
                    goods_weight_max = -int(value[i]["goodsnum"]) * (value[i]["weight_base"] - value[i]["weight_drift"]-5)
                change_weight_min = change_weight_min + goods_weight_min
                change_weight_max = change_weight_max + goods_weight_max
            change_weight[key]=[change_weight_min,change_weight_max]
        else:
            change_weight[key] = ""
    return change_weight


@csrf_exempt
def get_down_process(request):
    response_date={}
    process_size=cache.get('process_size')
    sum_size=cache.get('sum_size')
    response_date['output']=[process_size,sum_size]
    return HttpResponse(json.dumps(response_date), content_type="application/json charset=utf-8")
@csrf_exempt
def analyze_process(request):
    respons_date = {}
    date = json.loads(request.body.decode("utf8"))
    print(date)
    env=int(date["dev_env"])
    dev_id=int(date["dev_id"])
    login_user=date["login_user"]
    login_pw=date["login_pw"]
    union_id,online_status=get_dev_status(env,dev_id)
    sub_respons_date = []
    if union_id:
        if online_status == 0:
            sub_respons_date.append({'dev_status': "设备离线"})
            respons_date["output"] = sub_respons_date
            return HttpResponse(json.dumps(respons_date))
        else:
            frp_status=get_app_status(env,union_id,"frp-client-ssh")
            if frp_status=="stopped":
                frp_open_status, frp_open_tip = open_frp(env, dev_id, union_id)
                if frp_open_status == "Fail":
                    sub_respons_date.append({'dev_status': frp_open_tip})
                    respons_date["output"] = sub_respons_date
                    return HttpResponse(json.dumps(respons_date))
            get_goods_status, goods_date = get_goods_info(env, login_user, login_pw)
            if get_goods_status == "Fail":
                sub_respons_date.append({'dev_status': goods_date})
                respons_date["output"] = sub_respons_date
                return HttpResponse(json.dumps(respons_date))
            else:
                sub_respons_date.append({'dev_status': "Analyze ready"})
                respons_date["output"] = sub_respons_date
                return HttpResponse(json.dumps(respons_date))

    else:
        sub_respons_date.append({'dev_status': online_status})
        respons_date["output"] = sub_respons_date
        return HttpResponse(json.dumps(respons_date))
#公共函数，打开frp，获取设备状态，获取商品数据库
def get_app_status(env,union,app_type):
    if env==0:
        url = "http://10.4.32.114:8085/rrpc"
    elif env==1:
        url = "http://w.vegcloud.xyz:8085/rrpc"
    payload = "{\"devname\": \""+str(union)+"\", \"req\": {\"A\": 151}}"
    headers_frp = {
        'Content-Type': "application/json",
        'cache-control': "no-cache",
        'Postman-Token': "0b5b07b3-c756-4359-88b9-da388c58324d"
    }
    response_appstatus = requests.request("POST", url, data=payload, headers=headers_frp)
    app_status = json.loads(response_appstatus.text)
    if app_status["msg"].lower() == "success":
        for key,value in app_status["output"].items():
            if key==app_type:
                return value["state"]
def get_goods_info(env,erp_user,erp_pw):
    if env==0:
        web_login_url = "http://10.4.32.114:8080/login"
        web_query_goods_url = "http://10.4.32.114:8080/post_common_admin/"
        web_login_Referer = "http://10.4.32.114:8080/g/utstarcom"
        web_query_goods_Referer = "http://10.4.32.114:8080/main"
    elif env==1:
        web_login_url = "https://gosmart.ustar-ai.com/login"
        web_query_goods_url = "https://gosmart.ustar-ai.com/post_common_admin/"
        web_query_goods_Referer = "https://gosmart.ustar-ai.com"
        web_login_Referer = "https://gosmart.ustar-ai.com/g/utstarcom"
    cj = cookiejar.CookieJar()
    cookie_support = urllib.request.HTTPCookieProcessor(cj)
    opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)

    login_url = web_login_url
    headers_login = {'Referer': web_login_Referer,
                     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    postData_login = {'employee_id': erp_user, 'employee_pass': erp_pw}
    postData_login = urllib.parse.urlencode(postData_login, encoding='gb2312').encode('gb2312')
    request_login = urllib.request.Request(login_url, postData_login, headers_login)
    response_login = urllib.request.urlopen(request_login)
    login_text_org = response_login.read().decode()
    login_text = json.loads(login_text_org)
    login_token = login_text["token"]
    query_goods_url = web_query_goods_url
    headers_query_goods = {'Referer': web_query_goods_Referer,
                           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    postData_headers_query = {"access_token": login_token, "jwtauth_auth_ret_type": "json",
                              "command": "query_sku"}

    postData_headers_query = urllib.parse.urlencode(postData_headers_query, encoding='gb2312').encode(
        'gb2312')
    request_query_goods = urllib.request.Request(query_goods_url, postData_headers_query,
                                                 headers_query_goods)
    response_query_goods = urllib.request.urlopen(request_query_goods)
    query_goods_text_org = response_query_goods.read().decode()
    query_goods_text = json.loads(query_goods_text_org)
    if query_goods_text["msg"].lower() == "success":
        return   "Pass",query_goods_text["output"]
    else:
        return "Fail",query_goods_text["msg"]
def open_frp(env,dev_id,union_id):
    if env==0:
        url = "http://10.4.32.114:8085/rrpc"
    elif env==1:
        url = "http://w.vegcloud.xyz:8085/rrpc"
    try:
        if len(str(dev_id)) == 5:
            port_id = int(dev_id)
        else:
            port_id = "2" + str(dev_id)
        payload_frp = "{\"devname\": \"" + union_id + "\", \"req\": { \"A\": 152,\"P\": { \"appname\": \"frp-client-ssh\", \"action\": 4,\"port\":\"" + str(
            port_id) + "\" }}}"
        headers_frp = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            'Postman-Token': "0b5b07b3-c756-4359-88b9-da388c58324d"
        }
        response_frp_open = requests.request("POST", url, data=payload_frp, headers=headers_frp)
        frp_status = json.loads(response_frp_open.text)
        if frp_status["msg"].lower() == "success":
            pid = frp_status["output"]["pid"]
            for i in range(30):
                try:
                    payload_pid = "{\n    \"devname\": \"" + union_id + "\",\n    \"req\": {\n        \"A\": 153,\n        \"P\": {\n          \"pid\":\"" + pid + "\"\n        }\n    }\n}\n"
                    headers_pid = {
                        'Content-Type': "application/json",
                        'cache-control': "no-cache",
                        'Postman-Token': "20e0e8d2-28c2-4f7b-be6b-89b6b2451d60"
                    }
                    response_pid = requests.request("POST", url, data=payload_pid, headers=headers_pid)
                    pid_status = json.loads(response_pid.text)
                    if pid_status["msg"].lower() == "success":
                        if pid_status["output"]["state"] == "completed":
                            return "Pass","enable FRP successful"
                    else:
                        return "Fail",pid_status["msg"]
                except:
                    return "Fail","Query PID of enable FRP failure"
                time.sleep(5)
        else:
            return "Fail","PID request failure"
    except BaseException as e:
        print(e)
        return "Fail",e
def get_dev_status(env,dev_id):
    if env==1:
        login_url="http://gosmart.ustar-ai.com:8500/login"
        longin_ref="http://gosmart.ustar-ai.com:8500/login"
        dev_url="http://gosmart.ustar-ai.com:8500/api/query_dev"
        dev_ref="http://gosmart.ustar-ai.com:8500/main"
    elif env==0:
        login_url="http://10.4.32.114:8500/login"
        longin_ref="http://10.4.32.114:8500/login"
        dev_url="http://10.4.32.114:8500/api/query_dev"
        dev_ref="http://10.4.32.114:8500/main"
    try:
        cj = cookiejar.CookieJar()
        cookie_support = urllib.request.HTTPCookieProcessor(cj)
        opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
        urllib.request.install_opener(opener)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Referer': longin_ref}
        postData = {"employee_id": "HZ03881", "employee_pass": "NetRing1"}
        postData = urllib.parse.urlencode(postData, encoding='gb2312').encode('gb2312')
        request_login = urllib.request.Request(login_url, postData, headers)
        response = urllib.request.urlopen(request_login)
        login_text_org = response.read().decode()
        login_text = json.loads(login_text_org)
        login_token = login_text["token"]
        if login_text["result"].lower() == "success":
            time.sleep(1)
            postQueryDev = {"access_token": login_token, "command": "query_commodity_info","jwtauth_auth_ret_type": "json"}
            postQueryDev = urllib.parse.urlencode(postQueryDev, encoding='gb2312').encode('gb2312')
            request_QueryDev = urllib.request.Request(dev_url, postQueryDev, headers)
            response_QueryDev = urllib.request.urlopen(request_QueryDev)
            query_dev_org = response_QueryDev.read().decode()
            query_dev_org_dict = json.loads(query_dev_org)
            dev_info = query_dev_org_dict["output"]
            if query_dev_org_dict["msg"].lower() == "success":
                for key, value in dev_info.items():
                    if value["dev_id"]==dev_id:
                        return key,value["phy_state"]
                return None,"device is not exist"
            else:
                return None,"Get device info failure"
        else:
            return None,"login iot failure"
    except BaseException as e:
        return None, e

