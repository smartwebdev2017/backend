# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-21 20:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20170915_0704'),
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vin', models.CharField(max_length=17)),
                ('listing_make', models.CharField(max_length=20)),
                ('listing_model', models.CharField(max_length=30)),
                ('listing_trim', models.CharField(max_length=20)),
                ('listing_model_detail', models.CharField(max_length=30)),
                ('listing_year', models.IntegerField(max_length=4)),
                ('mileage', models.IntegerField(max_length=11)),
                ('city', models.CharField(max_length=20)),
                ('state', models.CharField(max_length=10)),
                ('listing_date', models.CharField(max_length=30)),
                ('price', models.CharField(max_length=11)),
                ('cond', models.CharField(max_length=10)),
                ('seller_type', models.CharField(max_length=15)),
                ('vhr_link', models.CharField(max_length=255)),
                ('listing_exterior_color', models.CharField(max_length=15)),
                ('listing_interior_color', models.CharField(max_length=15)),
                ('listing_transmission', models.CharField(max_length=15)),
                ('listing_transmission_detail', models.CharField(max_length=255)),
                ('listing_title', models.CharField(max_length=255)),
                ('listing_url', models.CharField(max_length=255)),
                ('listing_engine_size', models.CharField(max_length=10)),
                ('listing_description', models.CharField(max_length=255)),
                ('sold_state', models.IntegerField(max_length=1)),
                ('sold_date', models.CharField(max_length=30)),
                ('listing_body_type', models.CharField(max_length=20)),
                ('listing_drivetrain', models.CharField(max_length=10)),
                ('created', models.CharField(max_length=255)),
                ('updated', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(max_length=20)),
                ('url', models.CharField(max_length=255)),
                ('created', models.CharField(max_length=255)),
                ('updated', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state_name', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='car',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sites', to='api.Site'),
        ),
    ]
