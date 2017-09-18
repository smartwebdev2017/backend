from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    followers = models.ManyToManyField('self', related_name='followees', symmetrical=False)


class Post(models.Model):
    author = models.ForeignKey(User, related_name='posts')
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True, null=True)


class Photo(models.Model):
    post = models.ForeignKey(Post, related_name='photos')
    image = models.ImageField(upload_to="%Y/%m/%d")

class Site(models.Model):
    site_name = models.CharField(max_length=20)
    url = models.CharField(max_length=255)
    created = models.CharField(max_length=255)
    updated = models.CharField(max_length=255)

class Car(models.Model):
    #id = models.IntegerField()
    site = models.ForeignKey(Site, related_name='sites')
    vin = models.CharField(max_length=17)
    listing_make = models.CharField(max_length=20)
    listing_model = models.CharField(max_length=30)
    listing_trim = models.CharField(max_length=20)
    listing_model_detail = models.CharField(max_length=30)
    listing_year = models.IntegerField(max_length=4)
    mileage = models.IntegerField(max_length=11)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=10)
    listing_date = models.CharField(max_length=30)
    price = models.CharField(max_length=11)
    cond = models.CharField(max_length=10)
    seller_type = models.CharField(max_length=15)
    vhr_link = models.CharField(max_length=255)
    listing_exterior_color = models.CharField(max_length=15)
    listing_interior_color = models.CharField(max_length=15)
    listing_transmission = models.CharField(max_length=15)
    listing_transmission_detail = models.CharField(max_length=255)
    listing_title = models.CharField(max_length=255)
    listing_url = models.CharField(max_length=255)
    listing_engine_size = models.CharField(max_length=10)
    listing_description = models.CharField(max_length=255)
    sold_state = models.IntegerField(max_length=1)
    sold_date = models.CharField(max_length=30)
    listing_body_type = models.CharField(max_length=20)
    listing_drivetrain = models.CharField(max_length=10)
    created = models.CharField(max_length=255)
    updated = models.CharField(max_length=255)

class City(models.Model):
    city_name = models.CharField(max_length=20)

class State(models.Model):
    state_name = models.CharField(max_length=20)