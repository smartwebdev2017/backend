# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-25 01:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_retrycar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='listing_exterior_color',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='car',
            name='listing_interior_color',
            field=models.TextField(),
        ),
    ]
