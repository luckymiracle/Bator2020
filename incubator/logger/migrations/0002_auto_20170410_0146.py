# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-10 01:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dht',
            name='Humidity',
            field=models.FloatField(default=40),
        ),
        migrations.AlterField(
            model_name='dht',
            name='date_log',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='dht',
            name='temperature',
            field=models.FloatField(default=60),
        ),
    ]
