# Generated by Django 2.2.4 on 2019-08-28 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0038_auto_20181221_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='room_rate',
            field=models.TextField(blank=True, default=''),
        ),
    ]
