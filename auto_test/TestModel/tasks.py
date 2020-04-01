#-*- coding: UTF-8 -*-#-*- coding: UTF-8 -*-
from auto_test import celery_app as app
from datetime import date,time,timedelta,timezone,tzinfo,datetime
from auto_test.get_performance_date import get_performance
from auto_test.write_job_suite import operator_suite_log
from auto_test.mERP_Auto_Test import merp_auto_test
from auto_test.wifi_Auto_Test import wifi_auto_test
from auto_test.Get_SKU import gpa_operation
import json
import paramiko
import json
import re
import time



@app.task(track_started=True,name='get_cpu_mem_job')
def get_cpu_mem_process(dev_list):
    dev_id_list=dev_list
    #dev_id_list=[[2012,"1012018093000149","生产","arm"],[2030,"1012019010301781","生产","arm"]]
    dev_date={"2012":["1012018093000149","生产","arm"],"2001":["1012018071000020","测试","arm"],"1049":["1012018071000014","测试","arm"],"2003":["02c00081b27ae2bd","测试","nanopi"],"10061":["1012019010301847","测试","arm"],"12051":["1012019031900104","测试","arm"],"2017":["02c0008166531e3f","测试","nanopi"],"2030":["1012019010301781","生产","arm"],"3069":["1012019031900102","生产","arm"]}

    save_log = operator_suite_log("auto_test_log", "get_cpu_mem_job")
    case_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for i in range(len(dev_id_list)):
        dev_id = int(dev_id_list[i])
        dev_union_id=dev_date[str(dev_id)][0]
        dev_url = dev_date[str(dev_id)][1]
        dev_hard_type=dev_date[str(dev_id)][2]
        # 设置SSH登入端口号
        if len(str(dev_id)) < 5:
            sshid_org = "2" + str(dev_id)
            sshid = int(sshid_org)
        else:
            sshid = int(dev_id)
        # 获取打开FRP的url
        if dev_url == "测试":
            url = "http://10.4.32.114:8085/rrpc"
        elif dev_url == "生产":
            url = "http://w.vegcloud.xyz:8085/rrpc"
        # 设置SSH登入密码
        if dev_hard_type == "arm":
            sshname = "linaro"
        else:
            sshname = "pi"
        getperformance = get_performance(dev_union_id, dev_id, url, "auto_test_log", sshid, sshname)
        start_frp = getperformance.start_app()
        if start_frp =="Pass":
            getdb = getperformance.get_date()
            if type(getdb) == type((1, 2)):
                wrt_cpu = save_log.write_cpu_date(str(dev_id), getdb[0]["door"], getdb[0]["weigh"],
                                                  getdb[0]["weighcv_cm"], getdb[0]["weighcv_as"], getdb[0]["iotkit"],
                                                  getdb[0]["apps"], getdb[0]["alarm"], getdb[0]["monitor"],
                                                  getdb[0]["tts"], case_tm)
                wrt_mem = save_log.write_mem_date(str(dev_id), getdb[1]["door"], getdb[1]["weigh"],
                                                  getdb[1]["weighcv_cm"], getdb[1]["weighcv_as"], getdb[1]["iotkit"],
                                                  getdb[1]["apps"], getdb[1]["alarm"], getdb[1]["monitor"],
                                                  getdb[1]["tts"], case_tm)
                wrt_mem_summary = save_log.write_mem_summary_date(str(dev_id), getdb[2]["mem_total"],
                                                                  getdb[2]["mem_free"], getdb[2]["mem_use"],
                                                                  getdb[2]["mem_buff"], getdb[2]["remaind_space"],
                                                                  case_tm)
                if wrt_cpu == "Pass" and wrt_mem == "Pass" and wrt_mem_summary == "Pass":
                    save_log.write_case(dev_id, "get_cpu_mem_date", "pass", "pass", case_tm)
                else:
                    save_log.write_case(dev_id, "get_cpu_mem_date", "Fail", "write db fail", case_tm)
            else:
                save_log.write_case(dev_id, "get_cpu_mem_date", "Fail", getdb, case_tm)
        else:
            save_log.write_case(dev_id, "get_cpu_mem_date", "Fail", start_frp, case_tm)

@app.task(track_started=True,name='mERP_test_job')
def mERP_Auto_test(dev_id,env):
    if int(env)==0:
        login_url="10.4.32.114"
    elif int(env)==1:
        login_url="gosmart.ustar-ai.com"
    mERP_test=merp_auto_test(login_url,"HZ05791","76831213",int(env),"auto_test_log","mERP_test_job")
    barcode_list = ["6910000000013", "6910000000020", "6910000000037", "6910000000044", "6910000000051",
                    "6910000000068", "6910000000075", "6910000000082", "6910000000099", "910000000105",
                    "6910000000112", "6910000000129", "6910000000136", "6910000000143", "6910000000150"]
    dev_id=int(dev_id[0])
    dev_info_date=mERP_test.query_box_info(dev_id)
    template_box_model=dev_info_date["box_model"]
    template_weigh_type=dev_info_date["weigh_type"]
    dev_type=dev_info_date["dev_type"]
    if dev_type ==4:
        template_profile_dev_type="1"
    elif dev_type ==8:
        template_profile_dev_type = "2"

    query_end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    today_org=datetime.now()
    query_start_time_org = today_org-timedelta(days=15)
    query_start_his_alm_time_org=today_org-timedelta(days=3)
    query_start_his_alm_time=query_start_his_alm_time_org.strftime('%Y-%m-%d %H:%M:%S')
    query_start_time=query_start_time_org.strftime('%Y-%m-%d %H:%M:%S')
    create_tmplate_date = {"command": "add_dev_profile", "profile_dev_type":str(template_profile_dev_type), "box_model": str(template_box_model),
                           "profile_name": "auto_test", "weigh_type": str(template_weigh_type)}
    # 商品管理操作
    mERP_test.goods_operation(barcode_list)
    # 配置模板
    mERP_test.template_operation(create_tmplate_date, barcode_list, dev_info_date)
    #货柜操作
    mERP_test.box_goods_operation(dev_info_date, barcode_list)
    # 仓库管理
    mERP_test.stoke_management(barcode_list, dev_id, query_start_time, query_end_time)
    # 交易管理
    mERP_test.deal_order_count(query_start_time, query_end_time, dev_id)
    # 交易商品查询
    mERP_test.deal_goods_count(query_start_time, query_end_time, dev_id)
    # 退款查询
    mERP_test.resume_count(query_start_time, query_end_time, dev_id)
    # 退款申请查询
    mERP_test.resume_count_requerst(query_start_time, query_end_time, dev_id)
    mERP_test.date_count(query_start_time, query_end_time, dev_id)
    mERP_test.sales_goods_box(query_start_time, query_end_time, dev_id)
    mERP_test.sales_service_box(query_start_time, query_end_time, dev_id)
    # 货柜配置信息
    mERP_test.devid_attr_operation(dev_id)
    mERP_test.devid_audio_config(dev_id)
    mERP_test.init_box_config(dev_info_date)
    mERP_test.del_test_goods(barcode_list)
    mERP_test.weigh_type(dev_id)
    mERP_test.config_project_info(dev_id)
    #告警查询测试
    mERP_test.alarm_mode_base(query_start_his_alm_time, query_end_time,"HisAlarm")
    mERP_test.alarm_mode_base(query_start_his_alm_time, query_end_time, "CurAlarm")
    #告警订阅
    mERP_test.alarm_sub_test([dev_id])


@app.task(track_started=True,name='AS_Get_Sku')
def AS_Get_Sku(dev_list,env):
    sku_test=gpa_operation(env)
    with open('/django/venv/auto_test/static/goods_list.json', "r", encoding='utf-8') as f:
        goods_info = json.load(f)
    time.sleep(5)
    goods_list=goods_info["goods_info"]
    dev_id_list=dev_list
    for i in range(len(dev_id_list)):
        for j in range(len(goods_list)):
            if goods_list[j]["dev_id"]==int(dev_id_list[i]):
                sku_test.cp_sku(**goods_list[j])
                break

@app.task(track_started=True,name='network_test')
def wifi_Auto_test(dev_id,env):
    #仅生产及测试的第一组的设备
    if int(env)==0:
        login_url="10.4.32.114"
        wifi_test = wifi_auto_test(login_url, "ST00079", "12345", int(env), "auto_test_log", "network_test")
    elif int(env)==1:
        login_url="www.vegcloud.xyz"
        wifi_test = wifi_auto_test(login_url, "WE00069", "123456", int(env), "auto_test_log", "network_test")
    suite_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    save_log = operator_suite_log("auto_test_log", "network_test")
    dev_id = int(dev_id[0])
    wifi_test.devid_wifi_config(dev_id)

@app.task(track_started=True,name='CM_Get_Sku')
def CM_Get_Sku(dev_id_list,env):
    dev_id=dev_id_list[0]
    save_log=operator_suite_log("auto_test_log","CM_Get_Sku")
    counter_error=0
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
            int_id = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            trans_id = int(int_id.replace("-", ""))
            while True:
                case_tm = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                cmd_open_door = "curl -X POST \\" + "http://localhost:8086/door/1/open \\" + "-H \'Content-Type: application/json\' \\" + "-H \'Postman-Token: bb06b4e0-9459-40a4-b875-b39354cbb18a\' \\" + "-H \'cache-control: no-cache\' \\" + "-d \'{\"transid\":" + '"' + str(
                    trans_id) + '"' + ",\"lockid\": \"1-1-1\",\"user_type\": 1}\'"
                stdin, stdout, stderr = myclient.exec_command(cmd_open_door)
                time.sleep(20)
                open_lock_status_org = stdout.read().decode("utf-8")
                open_lock_status=json.loads(open_lock_status_org)
                if open_lock_status["msg"].lower()!="success":
                    save_log.write_case(dev_id,"open_lock_fail","Fail",open_lock_status["output"],case_tm)
                cmd = "cat " + "/vbg/root/weighcv-cm/log/" + str(trans_id) + ".txt"
                stdin, stdout, stderr = myclient.exec_command(cmd)
                open_goods_info_layer_1 = []
                open_goods_info_layer_2 = []
                open_goods_info_layer_3 = []
                open_goods_info_layer_4 = []
                close_goods_info_layer_1 = []
                close_goods_info_layer_2 = []
                close_goods_info_layer_3 = []
                close_goods_info_layer_4 = []
                open_goods_date=[]
                close_doods_date=[]
                while True:
                    line = stdout.readline()
                    if line:
                        open_goods_info_org = re.findall("CVOpenDoorDo OpenObjDetectInfo detectinfo=\s+(.+)", line)
                        close_goods_info_org = re.findall("CVCloseDoorDo CloseObjDetectInfo detectinfo=\s+(.+)", line)
                        if open_goods_info_org:
                            open_goods_info = open_goods_info_org[0]
                            open_goods_info_list = json.loads(open_goods_info)
                            for j in range(len(open_goods_info_list)):
                                if open_goods_info_list[j]["weighid"] == "010101":
                                    open_goods_info_layer_1_org = open_goods_info_list[j]["goodsinfo"]
                                    for j in range(len(open_goods_info_layer_1_org)):
                                        open_goods_info_layer_1_sub = {}
                                        open_goods_info_layer_1_sub = {
                                            open_goods_info_layer_1_org[j]["goodsid"]: open_goods_info_layer_1_org[j][
                                                "goodsnum"]}
                                        open_goods_info_layer_1.append(open_goods_info_layer_1_sub)
                                    open_goods_date.append(open_goods_info_layer_1)
                                elif open_goods_info_list[j]["weighid"] == "010201":
                                    open_goods_info_layer_2_org = open_goods_info_list[j]["goodsinfo"]
                                    for j in range(len(open_goods_info_layer_2_org)):
                                        open_goods_info_layer_2_sub = {}
                                        open_goods_info_layer_2_sub = {
                                            open_goods_info_layer_2_org[j]["goodsid"]: open_goods_info_layer_2_org[j][
                                                "goodsnum"]}
                                        open_goods_info_layer_2.append(open_goods_info_layer_2_sub)
                                    open_goods_date.append(open_goods_info_layer_2)
                                elif open_goods_info_list[j]["weighid"] == "010301":
                                    open_goods_info_layer_3_org = open_goods_info_list[j]["goodsinfo"]
                                    for j in range(len(open_goods_info_layer_3_org)):
                                        open_goods_info_layer_3_sub = {}
                                        open_goods_info_layer_3_sub = {
                                            open_goods_info_layer_3_org[j]["goodsid"]: open_goods_info_layer_3_org[j][
                                                "goodsnum"]}
                                        open_goods_info_layer_3.append(open_goods_info_layer_3_sub)
                                    open_goods_date.append(open_goods_info_layer_3)
                                elif open_goods_info_list[j]["weighid"] == "010401":
                                    open_goods_info_layer_4_org = open_goods_info_list[j]["goodsinfo"]
                                    for j in range(len(open_goods_info_layer_4_org)):
                                        open_goods_info_layer_4_sub = {}
                                        open_goods_info_layer_4_sub = {
                                            open_goods_info_layer_4_org[j]["goodsid"]: open_goods_info_layer_4_org[j][
                                                "goodsnum"]}
                                        open_goods_info_layer_4.append(open_goods_info_layer_4_sub)
                                    open_goods_date.append(open_goods_info_layer_4)
                        if close_goods_info_org:
                            close_goods_info = close_goods_info_org[0]
                            close_goods_info_list = json.loads(close_goods_info)
                            for j in range(len(close_goods_info_list)):
                                if close_goods_info_list[j]["weighid"] == "010101":
                                    close_goods_info_layer_1_org = close_goods_info_list[j]["goodsinfo"]
                                    for j in range(len(close_goods_info_layer_1_org)):
                                        close_goods_info_layer_1_sub = {}
                                        close_goods_info_layer_1_sub = {
                                            close_goods_info_layer_1_org[j]["goodsid"]: close_goods_info_layer_1_org[j][
                                                "goodsnum"]}
                                        close_goods_info_layer_1.append(close_goods_info_layer_1_sub)
                                    close_goods_date.append(close_goods_info_layer_1)
                                elif close_goods_info_list[j]["weighid"] == "010201":
                                    close_goods_info_layer_2_org = close_goods_info_list[j]["goodsinfo"]
                                    for j in range(len(close_goods_info_layer_2_org)):
                                        close_goods_info_layer_2_sub = {}
                                        close_goods_info_layer_2_sub = {
                                            close_goods_info_layer_2_org[j]["goodsid"]: close_goods_info_layer_2_org[j][
                                                "goodsnum"]}
                                        close_goods_info_layer_2.append(close_goods_info_layer_2_sub)
                                    close_goods_date.append(close_goods_info_layer_2)
                                elif close_goods_info_list[j]["weighid"] == "010301":
                                    close_goods_info_layer_3_org = close_goods_info_list[j]["goodsinfo"]
                                    for j in range(len(close_goods_info_layer_3_org)):
                                        close_goods_info_layer_3_sub = {}
                                        close_goods_info_layer_3_sub = {
                                            close_goods_info_layer_3_org[j]["goodsid"]: close_goods_info_layer_3_org[j][
                                                "goodsnum"]}
                                        close_goods_info_layer_3.append(close_goods_info_layer_3_sub)
                                    close_goods_date.append(close_goods_info_layer_3)
                                elif close_goods_info_list[j]["weighid"] == "010401":
                                    close_goods_info_layer_4_org = close_goods_info_list[j]["goodsinfo"]
                                    for j in range(len(close_goods_info_layer_4_org)):
                                        close_goods_info_layer_4_sub = {}
                                        close_goods_info_layer_4_sub = {
                                            close_goods_info_layer_4_org[j]["goodsid"]: close_goods_info_layer_4_org[j][
                                                "goodsnum"]}
                                        close_goods_info_layer_4.append(close_goods_info_layer_4_sub)
                                    close_goods_date.append(close_goods_info_layer_4)
                    else:
                        break
                for open_goods_info_layer in open_goods_date:
                    if not open_goods_info_layer:
                        counter_error +=1
                        save_log.write_case(dev_id, "open_detect", "Fail",str(trans_id), case_tm)
                for close_goods_info_layer in close_doods_date:
                    if not close_goods_info_layer:
                        counter_error +=1
                        save_log.write_case(dev_id, "open_detect", "Fail",str(trans_id), case_tm)
                if counter_error >10:
                    break
                time.sleep(120)
                trans_id +=1
        time.sleep(30)
    print(str(lp) + "次SSH登入失败")

















    
