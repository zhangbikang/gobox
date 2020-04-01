# Generated by Django 2.2.1 on 2019-05-29 06:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TestModel', '0002_auto_20190529_0621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case_log',
            name='job_log_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 6, 21, 52, 857450), null=True),
        ),
        migrations.AlterField(
            model_name='cpu_used',
            name='get_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 6, 21, 52, 854155), null=True),
        ),
        migrations.AlterField(
            model_name='mem_summary',
            name='get_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 6, 21, 52, 856060), null=True),
        ),
        migrations.AlterField(
            model_name='mem_used',
            name='get_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 6, 21, 52, 855257), null=True),
        ),
        migrations.AlterField(
            model_name='suite_status',
            name='job_run_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 6, 21, 52, 856745), null=True),
        ),
    ]