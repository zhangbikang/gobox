from django.contrib import admin
from TestModel.models import *

# Register your models here.
#class TagInline(admin.TabularInline):
    #model = Tag
class cpuadmin(admin.ModelAdmin):
    list_display = ("devid_id","door","weigh","weighcv_cm","weighcv_as","iotkit","apps","alarm","monitor","tts","get_time")
    search_fields = ('devid_id',)
    #inlines = [TagInline]
    #fieldsets=()
class memadmin(admin.ModelAdmin):
    list_display = ("devid_id","door","weigh","weighcv_cm","weighcv_as","iotkit","apps","alarm","monitor","tts","get_time")
    search_fields = ('devid_id',)
class memsummaryadmin(admin.ModelAdmin):
    list_display = ("devid_id","mem_total","mem_use","mem_free","mem_buff","remaind_space")
    search_fields = ('devid_id',)
class jobdateadmin(admin.ModelAdmin):
    list_display = ("job_suite_name","job_case_run_status","job_run_time")
    search_fields = ("job_suite_name",)
class joblogadmin(admin.ModelAdmin):
    list_display = ("devid_id","job_suite_name","job_cass_name","job_case_result","job_cass_log","job_log_time")
    search_fields = ("job_suite_name",)
admin.site.register(cpu_used,cpuadmin)
admin.site.register(mem_used,memadmin)
admin.site.register(mem_summary,memsummaryadmin)
admin.site.register(suite_status,jobdateadmin)
admin.site.register(case_log,joblogadmin)
