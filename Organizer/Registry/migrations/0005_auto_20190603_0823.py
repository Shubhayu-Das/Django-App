# Generated by Django 2.2.1 on 2019-06-03 08:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Registry', '0004_auto_20190603_0818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storedata',
            name='last_class_attended',
            field=models.DateField(default=datetime.date(2019, 6, 3)),
        ),
    ]
