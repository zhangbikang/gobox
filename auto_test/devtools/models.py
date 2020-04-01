from django.db import models

# Create your models here.

class down_load_process(models.Model):
    process_size=models.IntegerField()
    total_size=models.IntegerField()
    counter_size=models.IntegerField()
