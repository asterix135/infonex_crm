# Generated by Django 3.0.3 on 2020-02-21 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0040_auto_20200221_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterlistselections',
            name='title',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
