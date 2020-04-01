# Generated by Django 2.2.1 on 2019-06-01 23:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TestModel', '0012_auto_20190531_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case_log',
            name='job_log_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 6, 1, 23, 10, 7, 52979), null=True),
        ),
        migrations.AlterField(
            model_name='cpu_used',
            name='get_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 6, 1, 23, 10, 7, 49720), null=True),
        ),
        migrations.AlterField(
            model_name='mem_summary',
            name='get_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 6, 1, 23, 10, 7, 51560), null=True),
        ),
        migrations.AlterField(
            model_name='mem_used',
            name='get_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 6, 1, 23, 10, 7, 50600), null=True),
        ),
        migrations.AlterField(
            model_name='suite_status',
            name='job_run_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 6, 1, 23, 10, 7, 52250), null=True),
        ),
    ]
