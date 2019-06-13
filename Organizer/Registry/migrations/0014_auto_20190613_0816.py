# Generated by Django 2.2.1 on 2019-06-13 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Registry', '0013_auto_20190611_0805'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storedata',
            name='mac_address',
        ),
        migrations.AddField(
            model_name='storedata',
            name='unseen_file_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='storedata',
            name='unseen_message_count',
            field=models.IntegerField(default=0),
        ),
    ]