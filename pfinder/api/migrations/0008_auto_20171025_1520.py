# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-25 22:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20171024_1803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pcf',
            name='color',
            field=models.TextField(),
        ),
    ]
