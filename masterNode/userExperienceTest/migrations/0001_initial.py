# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompatibilityScript',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('script_path_ie', models.CharField(max_length=200, verbose_name='ie\u7684\u7528\u6237\u4f53\u9a8c\u6d4b\u8bd5\u811a\u672c\u7684\u8def\u5f84')),
                ('script_path_firefox', models.CharField(max_length=200, verbose_name='firefox\u7684\u7528\u6237\u4f53\u9a8c\u6d4b\u8bd5\u811a\u672c\u7684\u8def\u5f84')),
                ('script_path_chrome', models.CharField(max_length=200, verbose_name='chrome\u7684\u7528\u6237\u4f53\u9a8c\u6d4b\u8bd5\u811a\u672c\u7684\u8def\u5f84')),
            ],
        ),
        migrations.CreateModel(
            name='ImageInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('test_id', models.CharField(max_length=20, verbose_name='\u7528\u6237\u4f53\u9a8c\u6d4b\u8bd5\u7f16\u53f7')),
                ('browser', models.CharField(max_length=100, verbose_name='\u6d4f\u89c8\u5668')),
                ('image_name', models.CharField(max_length=200, verbose_name='\u622a\u56fe\u540d\u79f0')),
                ('image_url', models.CharField(max_length=200, verbose_name='\u622a\u56feurl')),
            ],
        ),
        migrations.CreateModel(
            name='ImageReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('test_id', models.CharField(max_length=20, verbose_name='\u7528\u6237\u4f53\u9a8c\u6d4b\u8bd5\u7f16\u53f7')),
                ('image_name', models.CharField(max_length=200, verbose_name='\u622a\u56fe\u540d\u79f0')),
                ('status', models.BooleanField(verbose_name='\u622a\u56fe\u662f\u5426\u6b63\u5e38')),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('exec_time', models.TimeField()),
                ('repeat_type', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('test_id', models.CharField(max_length=20, verbose_name='\u7528\u6237\u4f53\u9a8c\u6d4b\u8bd5\u7f16\u53f7')),
                ('reporter', models.CharField(max_length=100, verbose_name='\u62a5\u544a\u63d0\u4ea4\u4eba')),
                ('system', models.CharField(max_length=100, verbose_name='\u7cfb\u7edf')),
                ('sub_time', models.DateTimeField(auto_now=True, verbose_name='\u63d0\u4ea4\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='ReportPerBrowser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('test_id', models.CharField(max_length=20, verbose_name='\u7528\u6237\u4f53\u9a8c\u6d4b\u8bd5\u7f16\u53f7')),
                ('province', models.CharField(max_length=100, verbose_name='\u7701\u4efd')),
                ('city', models.CharField(max_length=100, verbose_name='\u57ce\u5e02')),
                ('total_num', models.IntegerField(verbose_name='\u6d4b\u8bd5\u7528\u4f8b\u6570\u76ee')),
                ('pass_num', models.IntegerField(verbose_name='\u901a\u8fc7\u6d4b\u8bd5\u7684\u6570\u76ee')),
                ('apdex', models.FloatField(verbose_name='Apdex')),
                ('browser', models.CharField(max_length=100, verbose_name='\u6d4f\u89c8\u5668')),
                ('report_url', models.CharField(max_length=200, verbose_name='\u62a5\u544aurl')),
            ],
        ),
        migrations.CreateModel(
            name='System',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='\u7cfb\u7edf')),
                ('english_name', models.CharField(max_length=100, verbose_name='\u7cfb\u7edf\u7684\u82f1\u6587\u540d\u79f0')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('executor', models.CharField(max_length=100, verbose_name='\u5de1\u68c0\u4eba')),
                ('province', models.CharField(max_length=100, verbose_name='\u7701\u4efd')),
                ('city', models.CharField(max_length=100, verbose_name='\u57ce\u5e02')),
                ('system', models.ForeignKey(to='userExperienceTest.System')),
            ],
        ),
        migrations.CreateModel(
            name='TestCase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='\u6d4b\u8bd5\u7528\u4f8b\u540d\u79f0')),
                ('content', models.TextField(verbose_name='\u6d4b\u8bd5\u7528\u4f8b')),
                ('description', models.TextField(verbose_name='\u6d4b\u8bd5\u7528\u4f8b\u63cf\u8ff0')),
                ('system', models.ForeignKey(to='userExperienceTest.System')),
            ],
        ),
        migrations.CreateModel(
            name='TestSuite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='\u6d4b\u8bd5\u5957\u4ef6\u540d\u79f0')),
                ('testcases', models.TextField(verbose_name='\u5305\u542b\u7684\u6d4b\u8bd5\u5957\u4ef6')),
                ('description', models.TextField(verbose_name='\u6d4b\u8bd5\u5957\u4ef6\u63cf\u8ff0')),
                ('system', models.ForeignKey(to='userExperienceTest.System')),
            ],
        ),
        migrations.AddField(
            model_name='task',
            name='test_suite',
            field=models.ForeignKey(to='userExperienceTest.TestSuite'),
        ),
        migrations.AddField(
            model_name='plan',
            name='task',
            field=models.ForeignKey(to='userExperienceTest.Task'),
        ),
        migrations.AddField(
            model_name='compatibilityscript',
            name='system',
            field=models.ForeignKey(to='userExperienceTest.System'),
        ),
    ]
