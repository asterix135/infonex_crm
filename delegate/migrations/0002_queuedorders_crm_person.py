# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-20 21:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0035_auto_20171019_1125'),
        ('delegate', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='queuedorders',
            name='crm_person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.Person'),
        ),
    ]
