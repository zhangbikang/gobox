"""django_1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import *
from django.urls import path
from django.contrib import admin
from TestModel import views
from devtools import views as tools_view

urlpatterns = [
    url(r'admin',admin.site.urls),
    url(r"^run_job_select",views.run_job_select),
    url(r"^get_db/",views.get_db),
    url(r"^get_cpu_date",views.get_cpu_date),
    #url(r"^get_mem_date", view.get_mem_date),
    url(r"select_test",views.select_test),
    url(r"query_job_status",views.query_job_status),
    url(r"query_case_log",views.query_case_log),
    url(r"query_suite_log", views.query_suite_log),
    url(r"ajax_case_log",views.ajax_case_log),
    url(r"ajax_query_log_detail",views.ajax_query_log_detail),
    url(r"dev_operator", tools_view.dev_operator),
    url(r"dev_attr",tools_view.dev_attr),
    url(r"ajax_attr_value",tools_view.ajax_attr_value),
    url(r"order_analyze", tools_view.order_analyze),
    url(r"analyze_process", tools_view.analyze_process),
    url(r"get_trans_id", tools_view.get_trans_id),
    url(r"get_down_process", tools_view.get_down_process),
    url(r'^',views.index)

]