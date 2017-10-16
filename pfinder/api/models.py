from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
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



class BSF(models.Model):
    #id = models.ManyToManyField(BSF_Options, related_name='options')
    vin = models.CharField(max_length=17)
    msrp = models.IntegerField(max_length=11)
    warranty_start = models.CharField(max_length=20)
    model_year = models.IntegerField(max_length=4)
    model_detail = models.TextField()
    color = models.TextField()
    production_month = models.CharField(max_length=7)
    interior = models.TextField()

class BSF_Options(models.Model):
    bsf = models.ForeignKey(BSF, related_name='options')
    code = models.CharField(max_length=11)
    value = models.TextField()

class VHF(models.Model):
    title_check = models.TextField()
    accident_check = models.TextField(blank=True, null=True)
    owners = models.TextField(blank=True, null=True)
    recall_count = models.IntegerField(max_length=11)

class VDF(models.Model):
    model_number = models.CharField(max_length=17)
    year = models.IntegerField(max_length = 4)
    model_detail = models.CharField(max_length=30)
    region = models.CharField(max_length=4)

class PCF(models.Model):
    longhood = models.IntegerField(max_length = 1)
    widebody = models.IntegerField(max_length = 1)
    pts = models.IntegerField(max_length = 1)
    pccb = models.IntegerField(max_length = 1)
    color = models.CharField(max_length=15)
    body_type = models.CharField(max_length=15)
    air_cooled = models.IntegerField(max_length=1)
    gap_to_msrp = models.FloatField()
    listing_age = models.IntegerField(max_length=1)
    lwb_seats = models.IntegerField(max_length=1)
    auto_trans = models.CharField(max_length = 15)
    option_code = models.TextField()
    option_description = models.TextField()
    placeholder = models.IntegerField(max_length = 2)
    produced_usa = models.IntegerField(max_length=11)
    produced_globally = models.IntegerField(max_length=11)
    same_counts = models.IntegerField(max_length=11)
    vid = models.CharField(max_length=6, null=True, blank=True)
class Car(models.Model):
    #id = models.IntegerField()
    site = models.ForeignKey(Site, related_name='sites')
    vin = models.ForeignKey(BSF, null=True, blank=True)

    #vin = models.ForeignKey(BSF, related_name='')
    vin_code = models.CharField(max_length=17, default='')
    listing_make = models.CharField(max_length=20)
    listing_model = models.CharField(max_length=30)
    listing_trim = models.CharField(max_length=20)
    listing_model_detail = models.CharField(max_length=30)
    listing_year = models.IntegerField(max_length=4)
    mileage = models.IntegerField(max_length=11)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=10)
    listing_date = models.CharField(max_length=30)
    price = models.IntegerField(max_length=11)
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
    listing_description = models.TextField()
    sold_state = models.IntegerField(max_length=1)
    sold_date = models.CharField(max_length=30)
    listing_body_type = models.CharField(max_length=20)
    listing_drivetrain = models.CharField(max_length=10)
    created = models.CharField(max_length=255)
    updated = models.CharField(max_length=255)
    vhf = models.ForeignKey(VHF, null=True, blank=True)
    vdf = models.ForeignKey(VDF, null=True, blank=True)
    pcf = models.ForeignKey(PCF, null=True, blank=True)

class City(models.Model):
    city_name = models.CharField(max_length=20)

class State(models.Model):
    state_name = models.CharField(max_length=20)



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)