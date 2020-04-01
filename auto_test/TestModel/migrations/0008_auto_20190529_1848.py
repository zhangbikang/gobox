# Generated by Django 2.2.1 on 2019-05-29 18:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TestModel', '0007_auto_20190529_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case_log',
            name='job_log_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 18, 48, 16, 542156), null=True),
        ),
        migrations.AlterField(
            model_name='cpu_used',
            name='get_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 18, 48, 16, 538798), null=True),
        ),
        migrations.AlterField(
            model_name='mem_summary',
            name='get_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 18, 48, 16, 540700), null=True),
        ),
        migrations.AlterField(
            model_name='mem_used',
            name='get_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 18, 48, 16, 539711), null=True),
        ),
        migrations.AlterField(
            model_name='suite_status',
            name='job_run_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 5, 29, 18, 48, 16, 541363), null=True),
        ),
    ]