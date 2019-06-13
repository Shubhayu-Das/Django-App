# Generated by Django 2.2.1 on 2019-06-11 08:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Registry', '0012_auto_20190608_1415'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storedata',
            name='fee_status',
        ),
        migrations.AddField(
            model_name='storedata',
            name='last_fees_paid',
            field=models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0)),
        ),
    ]