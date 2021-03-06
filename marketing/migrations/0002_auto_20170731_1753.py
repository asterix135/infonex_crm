# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-07-31 21:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedCell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cell_order', models.IntegerField()),
                ('content', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='uploadedfile',
            name='filetype',
        ),
        migrations.RemoveField(
            model_name='uploadedfile',
            name='first_row',
        ),
        migrations.RemoveField(
            model_name='uploadedrow',
            name='row',
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='num_columns',
            field=models.IntegerField(default=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='uploadedrow',
            name='row_is_first',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='uploadedrow',
            name='row_number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='uploadedcell',
            name='parent_row',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketing.UploadedRow'),
        ),
    ]
