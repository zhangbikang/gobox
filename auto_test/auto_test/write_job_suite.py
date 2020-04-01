#-*- coding: UTF-8 -*-#-*- coding: UTF-8 -*-
import pymysql
import time

class operator_suite_log():
    def __init__(self,db_name,suite_name):
        self.suite_name=suite_name
        self.db_name=db_name
    def write_suite(self,suite_status,suite_tm):
        try:
            db = pymysql.connect("localhost", "root", "st123456", self.db_name,charset="utf8")
            cursor = db.cursor()
            sql_command = "INSERT INTO TestModel_suite_status (job_suite_name, job_case_run_status,job_run_time) VALUES ('%s','%s','%s')" % (
            str(self.suite_name), str(suite_status), suite_tm)
            cursor.execute(sql_command)
            db.commit()
            db.close()
            add_id = cursor.lastrowid
            return add_id
        except:
            db.close
            return "write date to db failed"

    def update_suite(self,id):
        try:
            db = pymysql.connect("localhost", "root", "st123456", self.db_name,charset="utf8")
            cursor = db.cursor()
            sql_command = "UPDATE TestModel_suite_status SET job_case_run_status = 0 WHERE id = '%s'" % (id)
            cursor.execute(sql_command)
            db.commit()
            db.close()
            return "Pass"
        except:
            db.close
            return "update suite status faile"
    def write_case(self,devid_id,case_name,case_status,case_log,case_tm):
        try:
            db = pymysql.connect("localhost", "root", "st123456", self.db_name,charset="utf8")
            cursor = db.cursor()
            sql_command = "INSERT INTO TestModel_case_log (devid_id,job_suite_name, job_cass_name,job_case_result,job_cass_log,job_log_time) VALUES ('%s','%s','%s','%s','%s','%s')" % (
            devid_id, str(self.suite_name), str(case_name), str(case_status), pymysql.escape_string(case_log), case_tm)
            cursor.execute(sql_command)
            db.commit()
            db.close()
            return "Pass"
        except:
            db.close()
            print(case_log)


    def write_cpu_date(self,dev_id,door,weigh,weighcv_cm,weighcv_as,iotkit,apps,alarm,monitor,tts,wr_time):
        try:
            db = pymysql.connect("localhost", "root", "st123456", self.db_name,charset="utf8")
            cursor = db.cursor()
            sql_command = "INSERT INTO TestModel_cpu_used (devid_id, door,weigh,weighcv_cm,weighcv_as,iotkit,apps,alarm,monitor,tts,get_time) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (dev_id, door, weigh, weighcv_cm,weighcv_as,iotkit,apps, alarm, monitor,tts,wr_time)
            time.sleep(0.5)
            cursor.execute(sql_command)
            db.commit()
            db.close()
            return "Pass"
        except:
            db.close
            return "write cpu_date failure"
    def write_mem_date(self,dev_id,door,weigh,weighcv_cm,weighcv_as,iotkit,apps,alarm,monitor,tts,wr_time):
        try:
            db = pymysql.connect("localhost", "root", "st123456", self.db_name,charset="utf8")
            cursor = db.cursor()
            sql_command = "INSERT INTO TestModel_mem_used (devid_id, door,weigh,weighcv_cm,weighcv_as,iotkit,apps,alarm,monitor,tts,get_time) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (dev_id, door, weigh, weighcv_cm,weighcv_as,iotkit,apps, alarm, monitor,tts,wr_time)
            time.sleep(0.5)
            cursor.execute(sql_command)
            db.commit()
            db.close()
            return "Pass"
        except:
            db.close
            return "write mem_date failure"
    def write_mem_summary_date(self,dev_id,mem_total,mem_free,mem_use,mem_buff,remaind_space,wr_time):
        try:
            db = pymysql.connect("localhost", "root", "st123456", self.db_name,charset="utf8")
            cursor = db.cursor()
            sql_command = "INSERT INTO TestModel_mem_summary(devid_id,mem_total,mem_free,mem_use,mem_buff,remaind_space,get_time) VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (
                dev_id,mem_total,mem_free,mem_use,mem_buff,remaind_space,wr_time)
            time.sleep(0.5)
            cursor.execute(sql_command)
            db.commit()
            db.close()
            return "Pass"
        except:
            db.close()
            return "write mem_summary failure"
