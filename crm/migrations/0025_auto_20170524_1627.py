# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-24 20:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0024_auto_20170524_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='default_cat1',
            field=models.CharField(blank=True, choices=[('HR', 'HR'), ('FIN', 'FIN'), ('Industry', 'Industry'), ('Aboriginal', 'Aboriginal'), ('Gov', 'Gov'), ('USA', 'USA'), ('NA', 'None')], default='Industry', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='default_cat2',
            field=models.CharField(blank=True, choices=[('HR', 'HR'), ('FIN', 'FIN'), ('Industry', 'Industry'), ('Aboriginal', 'Aboriginal'), ('Gov', 'Gov'), ('USA', 'USA'), ('NA', 'None')], default='NA', max_length=15, null=True),
        ),
    ]