# Generated by Django 3.0.3 on 2020-06-29 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0041_masterlistselections_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changes',
            name='division1',
            field=models.CharField(blank=True, choices=[('1', '1 - Misc'), ('2', '2 - Misc'), ('3', '3 - Misc'), ('4', '4 - Misc'), ('5', '5 - Misc'), ('6', '6 - Misc'), ('A1', '1 - Accounting'), ('A2', '2 - Accounting'), ('A3', '3 - Accounting'), ('Aboriginal', 'Aboriginal'), ('Indig1', 'Indigenous ON/BC'), ('Indig2', 'Indigenous ROC'), ('FED 1', 'FED 1'), ('FED 2', 'FED 2'), ('FED 3', 'FED 3'), ('FED 4', 'FED 4'), ('USA', 'USA'), ('NA', 'Not Determined')], default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='changes',
            name='division2',
            field=models.CharField(blank=True, choices=[('1', '1 - Misc'), ('2', '2 - Misc'), ('3', '3 - Misc'), ('4', '4 - Misc'), ('5', '5 - Misc'), ('6', '6 - Misc'), ('A1', '1 - Accounting'), ('A2', '2 - Accounting'), ('A3', '3 - Accounting'), ('Aboriginal', 'Aboriginal'), ('Indig1', 'Indigenous ON/BC'), ('Indig2', 'Indigenous ROC'), ('FED 1', 'FED 1'), ('FED 2', 'FED 2'), ('FED 3', 'FED 3'), ('FED 4', 'FED 4'), ('USA', 'USA'), ('NA', 'Not Determined')], default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='person',
            name='division1',
            field=models.CharField(choices=[('1', '1 - Misc'), ('2', '2 - Misc'), ('3', '3 - Misc'), ('4', '4 - Misc'), ('5', '5 - Misc'), ('6', '6 - Misc'), ('A1', '1 - Accounting'), ('A2', '2 - Accounting'), ('A3', '3 - Accounting'), ('Aboriginal', 'Aboriginal'), ('Indig1', 'Indigenous ON/BC'), ('Indig2', 'Indigenous ROC'), ('FED 1', 'FED 1'), ('FED 2', 'FED 2'), ('FED 3', 'FED 3'), ('FED 4', 'FED 4'), ('USA', 'USA'), ('NA', 'Not Determined')], default='NA', max_length=20),
        ),
        migrations.AlterField(
            model_name='person',
            name='division2',
            field=models.CharField(blank=True, choices=[('1', '1 - Misc'), ('2', '2 - Misc'), ('3', '3 - Misc'), ('4', '4 - Misc'), ('5', '5 - Misc'), ('6', '6 - Misc'), ('A1', '1 - Accounting'), ('A2', '2 - Accounting'), ('A3', '3 - Accounting'), ('Aboriginal', 'Aboriginal'), ('Indig1', 'Indigenous ON/BC'), ('Indig2', 'Indigenous ROC'), ('FED 1', 'FED 1'), ('FED 2', 'FED 2'), ('FED 3', 'FED 3'), ('FED 4', 'FED 4'), ('USA', 'USA'), ('NA', 'Not Determined')], default='NA', max_length=20),
        ),
    ]
