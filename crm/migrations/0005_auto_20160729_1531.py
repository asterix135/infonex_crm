# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-29 19:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_person_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='company',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='person',
            name='main_category',
            field=models.CharField(choices=[('HR', 'HR'), ('FIN', 'FIN'), ('Industry', 'Industry'), ('Aboriginal', 'Aboriginal'), ('Gov', 'Gov'), ('USA', 'USA'), ('NA', 'None')], default='Industry', max_length=25),
        ),
        migrations.AlterField(
            model_name='person',
            name='main_category2',
            field=models.CharField(choices=[('HR', 'HR'), ('FIN', 'FIN'), ('Industry', 'Industry'), ('Aboriginal', 'Aboriginal'), ('Gov', 'Gov'), ('USA', 'USA'), ('NA', 'None')], default='NA', max_length=15),
        ),
        migrations.AlterField(
            model_name='person',
            name='title',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='reghistory',
            name='status',
            field=models.CharField(choices=[('DELEGATE', 'Paying Delegate'), ('SPEAKER', 'Speaker'), ('GUEST', 'Guest (non-revenue)'), ('SPONSOR', 'Sponsor Representative'), ('CANCEL', 'Cancelled Delegate'), ('OTHER', 'Other attendee')], default='DELEGATE', max_length=10),
        ),
    ]
