# Generated by Django 2.1 on 2018-08-29 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20180829_0127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='ip_address',
            field=models.GenericIPAddressField(),
        ),
    ]
