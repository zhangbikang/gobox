# Generated by Django 2.2.1 on 2019-05-29 18:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TestModel', '0008_auto_20190529_1848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case_log',
            name='job_log_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 18, 50, 36, 885557), null=True),
        ),
        migrations.AlterField(
            model_name='cpu_used',
            name='get_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 18, 50, 36, 882218), null=True),
        ),
        migrations.AlterField(
            model_name='mem_summary',
            name='get_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 18, 50, 36, 884131), null=True),
        ),
        migrations.AlterField(
            model_name='mem_used',
            name='get_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 18, 50, 36, 883151), null=True),
        ),
        migrations.AlterField(
            model_name='suite_status',
            name='job_run_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 18, 50, 36, 884815), null=True),
        ),
    ]
