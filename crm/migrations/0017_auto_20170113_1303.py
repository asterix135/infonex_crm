# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-13 18:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0016_auto_20170113_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='personallistselections',
            name='dept',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='personallistselections',
            name='company',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='personallistselections',
            name='industry',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
