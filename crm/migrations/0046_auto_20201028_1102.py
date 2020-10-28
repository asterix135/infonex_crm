# Generated by Django 3.0.8 on 2020-10-28 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0045_auto_20200730_1209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='fin_division1',
            field=models.CharField(choices=[('A1', 'FIN 1'), ('A2', 'FIN 2'), ('A3', 'FIN 3'), ('A4', 'FIN 4'), ('NA', 'Not Determined')], default='NA', max_length=20),
        ),
        migrations.AlterField(
            model_name='person',
            name='fin_division2',
            field=models.CharField(blank=True, choices=[('A1', 'FIN 1'), ('A2', 'FIN 2'), ('A3', 'FIN 3'), ('A4', 'FIN 4'), ('NA', 'Not Determined')], default='NA', max_length=20),
        ),
        migrations.AlterField(
            model_name='personallistselections',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.Person'),
        ),
    ]
