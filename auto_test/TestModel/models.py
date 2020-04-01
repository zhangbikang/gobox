from django.db import models
import django.utils.timezone as timezone
from datetime import *



# Create your models here.
class cpu_used(models.Model):
    id=models.AutoField(primary_key=True)
    devid_id=models.IntegerField()
    door=models.FloatField()
    weigh = models.FloatField()
    weighcv_cm = models.FloatField()
    weighcv_as = models.FloatField()
    iotkit = models.FloatField()
    apps = models.FloatField()
    alarm = models.FloatField()
    monitor = models.FloatField()
    tts = models.FloatField()
    get_time=models.DateTimeField(null=True,default=datetime.now(),blank=True)
    def __str__(self):
        return str(self.devid_id)
class mem_used(models.Model):
    id=models.AutoField(primary_key=True)
    devid_id=models.IntegerField()
    door=models.FloatField()
    weigh = models.FloatField()
    weighcv_cm = models.FloatField()
    weighcv_as = models.FloatField()
    iotkit = models.FloatField()
    apps = models.FloatField()
    alarm = models.FloatField()
    monitor = models.FloatField()
    tts = models.FloatField()
    get_time=models.DateTimeField(null=True,default=datetime.now(),blank=True)
    def __str__(self):
        return str(self.devid_id)
class mem_summary(models.Model):
    id=models.AutoField(primary_key=True)
    devid_id=models.IntegerField()
    mem_total=models.IntegerField()
    mem_free=models.IntegerField()
    mem_use=models.IntegerField()
    mem_buff=models.IntegerField()
    remaind_space=models.IntegerField()
    get_time=models.DateTimeField(null=True,default=datetime.now(),blank=True)
    def __str__(self):
        return str(self.devid_id)
class suite_status(models.Model):
    id=models.AutoField(primary_key=True)
    job_suite_name=models.CharField(max_length=50)
    job_case_run_status=models.IntegerField()
    job_run_time=models.DateTimeField(null=True,default=datetime.now(),blank=True)
    def __str__(self):
        return str(self.job_suite_name)
class case_log(models.Model):
    id=models.AutoField(primary_key=True)
    devid_id=models.IntegerField(blank=True,null=True)
    job_suite_name=models.CharField(max_length=50)
    job_cass_name=models.CharField(max_length=50)
    job_case_result=models.CharField(max_length=10)
    job_cass_log=models.TextField(null=True)
    job_mark=models.TextField(null=True)
    job_log_time=models.DateTimeField(null=True,default=datetime.now(),blank=True)
    def __str__(self):
        return str(self.job_suite_name)