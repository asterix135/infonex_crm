# Generated by Django 3.0.8 on 2020-07-30 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0043_auto_20200629_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='email_blocked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='person',
            name='fed_division1',
            field=models.CharField(choices=[('FED 1', 'FED 1'), ('FED 2', 'FED 2'), ('FED 3', 'FED 3'), ('FED 4', 'FED 4'), ('NA', 'Not Determined')], default='NA', max_length=20),
        ),
        migrations.AddField(
            model_name='person',
            name='fed_division2',
            field=models.CharField(blank=True, choices=[('FED 1', 'FED 1'), ('FED 2', 'FED 2'), ('FED 3', 'FED 3'), ('FED 4', 'FED 4'), ('NA', 'Not Determined')], default='NA', max_length=20),
        ),
        migrations.AddField(
            model_name='person',
            name='fin_division1',
            field=models.CharField(choices=[('A1', 'FIN-1'), ('A2', 'FIN-2'), ('A3', 'FIN-3'), ('A4', 'FIN-4'), ('NA', 'Not Determined')], default='NA', max_length=20),
        ),
        migrations.AddField(
            model_name='person',
            name='fin_division2',
            field=models.CharField(blank=True, choices=[('A1', 'FIN-1'), ('A2', 'FIN-2'), ('A3', 'FIN-3'), ('A4', 'FIN-4'), ('NA', 'Not Determined')], default='NA', max_length=20),
        ),
        migrations.AddField(
            model_name='person',
            name='indig_division',
            field=models.CharField(choices=[('Indig1', 'Indigenous ON/BC'), ('Indig2', 'Indigenous ROC'), ('NA', 'Not Determined')], default='NA', max_length=20),
        ),
        migrations.AddField(
            model_name='person',
            name='misc_division1',
            field=models.CharField(choices=[('Misc1', '1 - Misc'), ('Misc2', '2 - Misc'), ('Misc3', '3 - Misc'), ('Misc4', '4 - Misc'), ('NA', 'Not Determined')], default='NA', max_length=20),
        ),
        migrations.AddField(
            model_name='person',
            name='misc_division2',
            field=models.CharField(blank=True, choices=[('Misc1', '1 - Misc'), ('Misc2', '2 - Misc'), ('Misc3', '3 - Misc'), ('Misc4', '4 - Misc'), ('NA', 'Not Determined')], default='NA', max_length=20),
        ),
    ]
