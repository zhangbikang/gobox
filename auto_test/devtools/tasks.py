from django.test import TestCase
from auto_test import celery_app as app
from datetime import date,time,timedelta,timezone,tzinfo,datetime
import json
import paramiko
import json
import re
import time
# Create your tests here.

@app.task(track_started=True,name='down_load_log')
def down_load_log(local_file,remote_file):
    print("-----------------")
    sftp = paramiko.SFTPClient.from_transport(connect_client)
    sftp.get(remote_file, local_file,callable=file_size_update)
    myclient.close()
