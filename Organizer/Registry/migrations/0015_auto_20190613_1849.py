# Generated by Django 2.2.1 on 2019-06-13 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Registry', '0014_auto_20190613_0816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
