#-*- coding: UTF-8 -*-#-*- coding: UTF-8 -*-
from django.http import HttpResponse
from TestModel.models import cpu_used,mem_used,mem_summary,suite_status,case_log
from django.views.decorators.csrf import csrf_exempt
import json
#from .import get_performance
from auto_test.get_performance_date import get_performance
from auto_test.write_job_suite import operator_suite_log
import time
from django.contrib import messages
from django.shortcuts import render_to_response,render
from django.template import Context,RequestContext
from TestModel import tasks
from django_celery_results.models import TaskResult
from auto_test import celery_app as app


def index(request):
    return render_to_response("home.html")
def get_db(request):
    return render_to_response("select_query.html")
@csrf_exempt
def get_cpu_date(request):
    request.encoding="utf-8"
    date_dict={}
    cpu_date={}
    mem_date={}
    mem_summary_date={}
    door_cpu_list=[]
    weigh_cpu_list = []
    weighcv_cm_cpu_list = []
    weighcv_as_cpu_list = []
    iotkit_cpu_list = []
    apps_cpu_list = []
    alarm_cpu_list = []
    monitor_cpu_list = []
    tts_cpu_list = []
    door_mem_list=[]
    weigh_mem_list = []
    weighcv_cm_mem_list = []
    weighcv_as_mem_list = []
    iotkit_mem_list = []
    apps_mem_list = []
    alarm_mem_list = []
    monitor_mem_list = []
    tts_mem_list = []
    mem_total=[]
    mem_free=[]
    mem_use=[]
    mem_buff=[]
    remaind_space=[]
    respons_date = {}
    date = json.loads(request.body.decode("utf8"))
    dev_id = date["dev_id"]
    start_time=date["start_time"]
    end_time=date["end_time"]
    date_list_cpu=cpu_used.objects.filter(get_time__range=(start_time, end_time),devid_id=dev_id)
    date_list_mem=mem_used.objects.filter(get_time__range=(start_time, end_time),devid_id=dev_id)
    date_list_summary=mem_summary.objects.filter(get_time__range=(start_time,end_time),devid_id=dev_id)
    if date_list_cpu:
        for var in date_list_cpu:
            door_cpu_list.append(var.door)
            weigh_cpu_list.append(var.weigh)
            weighcv_cm_cpu_list.append(var.weighcv_cm)
            weighcv_as_cpu_list.append(var.weighcv_as)
            iotkit_cpu_list.append(var.iotkit)
            apps_cpu_list.append(var.apps)
            alarm_cpu_list.append(var.alarm)
            monitor_cpu_list.append(var.monitor)
            tts_cpu_list.append(var.tts)
        cpu_date["door_list"]=door_cpu_list
        cpu_date["weigh_list"]=weigh_cpu_list
        cpu_date["weighcv_cm_list"]=weighcv_cm_cpu_list
        cpu_date["weighcv_as_list"]=weighcv_as_cpu_list
        cpu_date["iotkit_list"]=iotkit_cpu_list
        cpu_date["apps_list"] = apps_cpu_list
        cpu_date["alarm_list"] = alarm_cpu_list
        cpu_date["monitor_list"] = monitor_cpu_list
        cpu_date["tts_list"] = tts_cpu_list
    if date_list_mem:
        for var in date_list_mem:
            door_mem_list.append(var.door)
            weigh_mem_list.append(var.weigh)
            weighcv_cm_mem_list.append(var.weighcv_cm)
            weighcv_as_mem_list.append(var.weighcv_as)
            iotkit_mem_list.append(var.iotkit)
            apps_mem_list.append(var.apps)
            alarm_mem_list.append(var.alarm)
            monitor_mem_list.append(var.monitor)
            tts_mem_list.append(var.tts)
        mem_date["door_list"]=door_mem_list
        mem_date["weigh_list"]=weigh_mem_list
        mem_date["weighcv_cm_list"]=weighcv_cm_mem_list
        mem_date["weighcv_as_list"]=weighcv_as_mem_list
        mem_date["iotkit_list"]=iotkit_mem_list
        mem_date["apps_list"] = apps_mem_list
        mem_date["alarm_list"] = alarm_mem_list
        mem_date["monitor_list"] = monitor_mem_list
        mem_date["tts_list"] = tts_mem_list
    if date_list_summary:
        for var_summay in date_list_summary:
            mem_total.append(var_summay.mem_total)
            mem_free.append(var_summay.mem_free)
            mem_use.append(var_summay.mem_use)
            mem_buff.append(var_summay.mem_buff)
            remaind_space.append(var_summay.remaind_space)
        mem_summary_date["mem_total"] = mem_total
        mem_summary_date["mem_free"] = mem_free
        mem_summary_date["mem_use"] = mem_use
        mem_summary_date["mem_buff"] = mem_buff
        mem_summary_date["remaind_space"] = remaind_space
    date_dict["dev_id"]=dev_id
    date_dict["cpu_date"]=cpu_date
    date_dict["mem_date"]=mem_date
    date_dict["mem_summary_date"]=mem_summary_date
    respons_date["output"]=date_dict
    return HttpResponse(json.dumps(respons_date))
@csrf_exempt
def select_test(request):
    return render_to_response("config_query_job.html")
@csrf_exempt
def get_cpu_mem_job(request):
    respons_date={}
    date=json.loads(request.body.decode("utf8"))
    tasks.get_cpu_mem_process.delay()
    respons_date["info"]="success"
    return HttpResponse(json.dumps(respons_date))
@csrf_exempt
def query_job_status(request):
    respons_date = {}
    date = json.loads(request.body.decode("utf8"))
    job_name_list = date["job_name"]
    start_time=date["start_time"]
    end_time=date["end_time"]
    job_status=date["job_stats"]
    if not job_status:
        if job_name_list:
            query_job_result = []
            for i in range(len(job_name_list)):
                job_actual_status_list = []
                job_actual_runtime_list = []
                job_status_id_list = []
                job_actual_name_list=[]
                job_middle_dict = {}
                date_job_status_list = TaskResult.objects.filter(date_done__range=(start_time, end_time),task_name=job_name_list[i])
                for var in date_job_status_list:
                    job_actual_status_list.append(var.status)
                    job_actual_runtime_list.append(var.date_done.strftime('%Y-%m-%d %H:%M:%S'))
                    job_status_id_list.append(var.id)
                    job_actual_name_list.append(var.task_name)
                job_middle_dict["name"] = job_actual_name_list
                job_middle_dict["status"] = job_actual_status_list
                job_middle_dict["time"] = job_actual_runtime_list
                job_middle_dict["id"] = job_status_id_list
                query_job_result.append(job_middle_dict)
            respons_date["output"] = query_job_result
            return HttpResponse(json.dumps(respons_date))
        else:
            query_job_result = []
            job_actual_status_list = []
            job_actual_runtime_list = []
            job_status_id_list = []
            job_actual_name_list = []
            job_middle_dict = {}
            date_job_status_list = TaskResult.objects.filter(date_done__range=(start_time, end_time))
            for var in date_job_status_list:
                job_actual_status_list.append(var.status)
                job_actual_runtime_list.append(var.date_done.strftime('%Y-%m-%d %H:%M:%S'))
                job_status_id_list.append(var.id)
                job_actual_name_list.append(var.task_name)
            job_middle_dict["name"] = job_actual_name_list
            job_middle_dict["status"] = job_actual_status_list
            job_middle_dict["time"] = job_actual_runtime_list
            job_middle_dict["id"] = job_status_id_list
            query_job_result.append(job_middle_dict)
            respons_date["output"] = query_job_result
            return HttpResponse(json.dumps(respons_date))
    elif not job_name_list:
        if not job_status:
            query_job_result = []
            job_actual_status_list = []
            job_actual_runtime_list = []
            job_status_id_list = []
            job_actual_name_list = []
            job_middle_dict = {}
            date_job_status_list = TaskResult.objects.filter(date_done__range=(start_time, end_time))
            for var in date_job_status_list:
                job_actual_status_list.append(var.status)
                job_actual_runtime_list.append(var.date_done.strftime('%Y-%m-%d %H:%M:%S'))
                job_status_id_list.append(var.id)
                job_actual_name_list.append(var.task_name)
            job_middle_dict["name"] = job_actual_name_list
            job_middle_dict["status"] = job_actual_status_list
            job_middle_dict["time"] = job_actual_runtime_list
            job_middle_dict["id"] = job_status_id_list
            query_job_result.append(job_middle_dict)
            respons_date["output"] = query_job_result
            return HttpResponse(json.dumps(respons_date))
        else:
            query_job_result = []
            job_actual_status_list = []
            job_actual_runtime_list = []
            job_status_id_list = []
            job_actual_name_list = []
            job_middle_dict = {}
            date_job_status_list = TaskResult.objects.filter(date_done__range=(start_time, end_time),status__in=job_status)
            for var in date_job_status_list:
                job_actual_status_list.append(var.status)
                job_actual_runtime_list.append(var.date_done.strftime('%Y-%m-%d %H:%M:%S'))
                job_status_id_list.append(var.id)
                job_actual_name_list.append(var.task_name)
            job_middle_dict["name"] = job_actual_name_list
            job_middle_dict["status"] = job_actual_status_list
            job_middle_dict["time"] = job_actual_runtime_list
            job_middle_dict["id"] = job_status_id_list
            query_job_result.append(job_middle_dict)
            respons_date["output"] = query_job_result
            return HttpResponse(json.dumps(respons_date))
    else:
        query_job_result = []
        for i in range(len(job_name_list)):
            job_actual_status_list = []
            job_actual_runtime_list = []
            job_status_id_list = []
            job_actual_name_list = []
            job_middle_dict = {}
            date_job_status_list = TaskResult.objects.filter(date_done__range=(start_time, end_time),task_name=job_name_list[i],status__in=job_status)
            for var in date_job_status_list:
                job_actual_status_list.append(var.status)
                job_actual_runtime_list.append(var.date_done.strftime('%Y-%m-%d %H:%M:%S'))
                job_status_id_list.append(var.id)
                job_actual_name_list.append(var.task_name)
            job_middle_dict["name"] = job_actual_name_list
            job_middle_dict["status"] = job_actual_status_list
            job_middle_dict["time"] = job_actual_runtime_list
            job_middle_dict["id"] = job_status_id_list
            query_job_result.append(job_middle_dict)
        respons_date["output"] = query_job_result
        return HttpResponse(json.dumps(respons_date))
@csrf_exempt
def query_case_log(request):
    return render_to_response("case_log_query.html")
def query_suite_log(request):
    return render_to_response("suite_log_query.html")
@csrf_exempt
def ajax_case_log(request):
    respons_date = {}
    date = json.loads(request.body.decode("utf8"))
    job_name_list = date["job_list"]
    start_time=date["start_time"]
    end_time=date["end_time"]
    case_status=date["case_status"]
    if not case_status:
        if job_name_list:
            job_case_date_list_org = []
            for i in range(len(job_name_list)):
                date_case_log_list = case_log.objects.filter(job_log_time__range=(start_time, end_time),job_suite_name=job_name_list[i])
                for var in date_case_log_list:
                    job_case_date = {}
                    job_case_date["devid_id"]=var.devid_id
                    job_case_date["case_id"] = var.id
                    job_case_date["job_suite_name"] = var.job_suite_name
                    job_case_date["job_case_name"] = var.job_cass_name
                    job_case_date["job_case_result"] = var.job_case_result
                    job_case_date["create_time"]=var.job_log_time.strftime('%Y-%m-%d %H:%M:%S')
                    job_case_date_list_org.append(job_case_date)
            respons_date["output"] = job_case_date_list_org
            return HttpResponse(json.dumps(respons_date))
        else:
            job_case_date_list_org = []
            date_case_log_list = case_log.objects.filter(job_log_time__range=(start_time, end_time))
            for var in date_case_log_list:
                job_case_date = {}
                job_case_date["devid_id"] = var.devid_id
                job_case_date["case_id"] = var.id
                job_case_date["job_suite_name"] = var.job_suite_name
                job_case_date["job_case_name"] = var.job_cass_name
                job_case_date["job_case_result"] = var.job_case_result
                job_case_date["create_time"] = var.job_log_time.strftime('%Y-%m-%d %H:%M:%S')
                job_case_date_list_org.append(job_case_date)
            respons_date["output"] = job_case_date_list_org
            return HttpResponse(json.dumps(respons_date))
    if not job_name_list:
        if case_status:
            job_case_date_list_org = []
            job_case_date = {}
            date_case_log_list = case_log.objects.filter(job_log_time__range=(start_time, end_time),job_case_result__in=case_status)
            for var in date_case_log_list:
                job_case_date = {}
                job_case_date["devid_id"] = var.devid_id
                job_case_date["case_id"] = var.id
                job_case_date["job_suite_name"] = var.job_suite_name
                job_case_date["job_case_name"] = var.job_cass_name
                job_case_date["job_case_result"] = var.job_case_result
                job_case_date["create_time"] = var.job_log_time.strftime('%Y-%m-%d %H:%M:%S')
                job_case_date_list_org.append(job_case_date)
            respons_date["output"] = job_case_date_list_org
            return HttpResponse(json.dumps(respons_date))
        else:
            job_case_date_list_org = []
            date_case_log_list = case_log.objects.filter(job_log_time__range=(start_time, end_time))
            for var in date_case_log_list:
                job_case_date = {}
                job_case_date["devid_id"] = var.devid_id
                job_case_date["case_id"] = var.id
                job_case_date["job_suite_name"] = var.job_suite_name
                job_case_date["job_case_name"] = var.job_cass_name
                job_case_date["job_case_result"] = var.job_case_result
                job_case_date["create_time"] = var.job_log_time.strftime('%Y-%m-%d %H:%M:%S')
                job_case_date_list_org.append(job_case_date)
            respons_date["output"] = job_case_date_list_org
            return HttpResponse(json.dumps(respons_date))
    else:
        job_case_date_list_org = []
        for i in range(len(job_name_list)):
            date_case_log_list = case_log.objects.filter(job_log_time__range=(start_time, end_time), job_suite_name=job_name_list[i],job_case_result__in=case_status)
            for var in date_case_log_list:
                job_case_date = {}
                job_case_date["devid_id"] = var.devid_id
                job_case_date["case_id"] = var.id
                job_case_date["job_suite_name"] = var.job_suite_name
                job_case_date["job_case_name"] = var.job_cass_name
                job_case_date["job_case_result"] = var.job_case_result
                job_case_date["create_time"] = var.job_log_time.strftime('%Y-%m-%d %H:%M:%S')
                job_case_date_list_org.append(job_case_date)
        respons_date["output"] = job_case_date_list_org
        return HttpResponse(json.dumps(respons_date))
@csrf_exempt
def ajax_query_log_detail(request):
    respons_date = {}
    date = json.loads(request.body.decode("utf8"))
    if date["query_type"] =="case_log":
        if date["query_operation"]=="case_info":
            case_id = date["query_id"]
            date_case_log_list = case_log.objects.filter(id=case_id)
            for var in date_case_log_list:
                respons_date["info"] = var.job_cass_log
            return HttpResponse(json.dumps(respons_date))
    elif date["query_type"]=="suite_log":
        if date["query_operation"]=="suite_info":
            suite_id=date["query_id"]
            date_suit_log_info=TaskResult.objects.filter(id=suite_id)
            for var in date_suit_log_info:
                respons_date["info"]=var.traceback
            return HttpResponse(json.dumps(respons_date))
        elif date["query_operation"] == "suite_operation":
            suite_id = date["query_id"]
            date_suit_task_id=TaskResult.objects.filter(id=suite_id)
            for var in date_suit_task_id:
                task_id=var.task_id
            app.control.revoke(task_id, terminate=True)
            respons_date["info"]=task_id +"停止成功"
            return HttpResponse(json.dumps(respons_date))
@csrf_exempt
def run_job_select(request):
    respons_date={}
    date=json.loads(request.body.decode("utf8"))
    print(date)
    job_id=date["job_name"]
    dev_list=date["dev_list"]
    env=date["dev_env"]
    if job_id=="get_cpu_mem_job":
        tasks.get_cpu_mem_process.delay(dev_list)
        respons_date["info"] = "success"
        return HttpResponse(json.dumps(respons_date))
    elif job_id=="mERP_AutoTest":
        tasks.mERP_Auto_test.delay(dev_list,env)
        respons_date["info"] = "success"
        return HttpResponse(json.dumps(respons_date))
    elif job_id=="network_test":
        tasks.wifi_Auto_test.delay(dev_list,env)
        respons_date["info"] = "success"
        return HttpResponse(json.dumps(respons_date))
    elif job_id=="AS_Get_Sku":
        tasks.AS_Get_Sku.delay(dev_list,env)
        respons_date["info"] = "success"
        return HttpResponse(json.dumps(respons_date))
    elif job_id=="CM_Get_Sku":
        tasks.CM_Get_Sku.delay(dev_list,env)
        respons_date["info"] = "success"
        return HttpResponse(json.dumps(respons_date))
























