"""masterNode URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from masterNode import settings
from django.conf.urls.static import static
from userExperienceTest import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^home/', views.home),
    url(r'^result/$', views.result),
    url(r'^imageresult/(?P<test_id>\d+)/(?P<browser>\w+)/$', views.image_result, name='imageresult'),
    url(r'^upload/$', views.upload),
    url(r'^uploadreport/', views.upload_report),
    url(r'^success/$', views.success),
    url(r'^search/', views.search, name='search'),
    url(r'^selectsystem/', views.select_system),

    url(r'^addcompatibilitytest/', views.add_compatibility_test),
    url(r'^createcompatibilitytestscript/', views.create_compatibility_test_script),
    url(r'^createcompatibilitytestscriptsuccess/', views.create_compatibility_test_script_success),
    url(r'^createcompatibilitytesttask/', views.create_compatibility_test_task),
    url(r'^compatibilitytest/', views.compatibility_test),

    url(r'^export/', views.export),
    url(r'^cluster/', views.cluster_status),

    url(r'^plans/', views.plan_list),
    url(r'^addplan/', views.add_plan),
    url(r'^createplan/', views.create_plan),
    url(r'^createplansuccess1/', views.create_plan_success1),
    url(r'^createplansuccess2/', views.create_plan_success2),

    url(r'^testsuites/', views.testsuite_list),
    url(r'^addtestsuite/', views.add_testsuite),
    url(r'^createtestsuite/', views.create_testsuite),
    url(r'^createtestsuitesuccess/', views.create_testsuite_success),
    url(r'^/testsuite/(?P<testsuite_id>[0-9]+)/$', views.testsuite_detail, name="testsuitedetail"),

    url(r'^testcases/', views.testcase_list),
    url(r'^addtestcase/', views.add_testcase),
    url(r'^createtestcase/', views.create_testcase),
    url(r'^createtestcasesuccess/', views.create_testcase_success),
    url(r'^/testcase/(?P<testcase_id>[0-9]+)/$', views.testcase_detail, name="testcasedetail"),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
