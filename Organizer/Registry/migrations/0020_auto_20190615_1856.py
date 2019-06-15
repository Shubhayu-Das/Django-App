# Generated by Django 2.2.1 on 2019-06-15 13:26

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Registry', '0019_auto_20190615_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='datePosted',
            field=models.DateTimeField(default=datetime.datetime(1969, 12, 31, 18, 7, tzinfo=utc), verbose_name='Date Posted: '),
        ),
        migrations.AlterField(
            model_name='storedata',
            name='last_fees_paid',
            field=models.DateTimeField(default=datetime.datetime(1969, 12, 31, 18, 7, tzinfo=utc)),
        ),
    ]
