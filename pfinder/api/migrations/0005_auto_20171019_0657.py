# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-19 13:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_pcf_model_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pcf',
            name='model_number',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
