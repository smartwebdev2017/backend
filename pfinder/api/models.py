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
    site_name = models.CharField(max_length=20,null=True, blank=True)
    url = models.CharField(max_length=255,null=True, blank=True)
    created = models.CharField(max_length=255,null=True, blank=True)
    updated = models.CharField(max_length=255,null=True, blank=True)



class BSF(models.Model):
    #id = models.ManyToManyField(BSF_Options, related_name='options')
    vin = models.CharField(max_length=17)
    msrp = models.IntegerField(max_length=11)
    warranty_start = models.CharField(max_length=20,null=True, blank=True)
    model_year = models.IntegerField(max_length=4)
    model_detail = models.TextField()
    color = models.TextField()
    production_month = models.DateField(max_length=10)
    interior = models.TextField()

class BSF_Options(models.Model):
    bsf = models.ForeignKey(BSF, related_name='options')
    code = models.CharField(max_length=11)
    value = models.TextField()

class VHF(models.Model):
    title_check = models.TextField(null=True, blank=True)
    accident_check = models.TextField(blank=True, null=True)
    owners = models.TextField(blank=True, null=True)
    recall_count = models.IntegerField(max_length=11,null=True, blank=True)

class VDF(models.Model):
    model_number = models.CharField(max_length=17,null=True, blank=True)
    year = models.IntegerField(max_length = 4,null=True, blank=True)
    model_detail = models.CharField(max_length=30,null=True, blank=True)
    region = models.CharField(max_length=4,null=True, blank=True)

class PCF(models.Model):
    longhood = models.IntegerField(max_length = 1,null=True, blank=True)
    widebody = models.IntegerField(max_length = 1,null=True, blank=True)
    pts = models.IntegerField(max_length = 1,null=True, blank=True)
    pccb = models.IntegerField(max_length = 1,null=True, blank=True)
    color = models.TextField(null=True, blank=True)
    body_type = models.CharField(max_length=15,null=True, blank=True)
    air_cooled = models.IntegerField(max_length=1,null=True, blank=True)
    gap_to_msrp = models.FloatField(null=True, blank=True)
    listing_age = models.IntegerField(max_length=1,null=True, blank=True)
    lwb_seats = models.IntegerField(max_length=1,null=True, blank=True)
    auto_trans = models.CharField(max_length = 15,null=True, blank=True)
    option_code = models.TextField(null=True, blank=True)
    option_description = models.TextField(null=True, blank=True)
    placeholder = models.IntegerField(max_length = 2,null=True, blank=True)
    produced_usa = models.IntegerField(max_length=11,null=True, blank=True)
    produced_globally = models.IntegerField(max_length=11,null=True, blank=True)
    same_counts = models.IntegerField(max_length=11,null=True, blank=True)
    model_number = models.CharField(max_length=5, null=True, blank=True)
    vid = models.CharField(max_length=6)

class Car(models.Model):
    #id = models.IntegerField()
    site = models.ForeignKey(Site, null=True, blank=True)
    vin = models.ForeignKey(BSF, null=True, blank=True)

    #vin = models.ForeignKey(BSF, related_name='')
    vin_code = models.CharField(max_length=17, null=True, blank=True)
    listing_make = models.CharField(max_length=20, null=True, blank=True)
    listing_model = models.CharField(max_length=30, null=True, blank=True)
    listing_trim = models.CharField(max_length=20, null=True, blank=True)
    listing_model_detail = models.CharField(max_length=30, null=True, blank=True)
    listing_year = models.IntegerField(max_length=4, null=True, blank=True)
    mileage = models.IntegerField(max_length=11, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    state = models.CharField(max_length=10, null=True, blank=True)
    listing_date = models.DateField(max_length=255)
    price = models.IntegerField(max_length=11, null=True, blank=True)
    cond = models.CharField(max_length=10, null=True, blank=True)
    seller_type = models.CharField(max_length=15, null=True, blank=True)
    vhr_link = models.CharField(max_length=255, null=True, blank=True)
    listing_exterior_color = models.TextField(null=True, blank=True)
    listing_interior_color = models.TextField(null=True, blank=True)
    listing_transmission = models.CharField(max_length=15, null=True, blank=True)
    listing_transmission_detail = models.CharField(max_length=255, null=True, blank=True)
    listing_title = models.CharField(max_length=255, null=True, blank=True)
    listing_url = models.CharField(max_length=255, null=True, blank=True)
    listing_engine_size = models.CharField(max_length=10, null=True, blank=True)
    listing_description = models.TextField(null=True, blank=True)
    sold_state = models.IntegerField(max_length=1, null=True, blank=True)
    sold_date = models.DateField(max_length=30, null=True, blank=True)
    listing_body_type = models.CharField(max_length=20, null=True, blank=True)
    listing_drivetrain = models.CharField(max_length=10, null=True, blank=True)
    created = models.DateField(max_length=255)
    updated = models.DateField(max_length=255)
    vhf = models.ForeignKey(VHF, null=True, blank=True)
    vdf = models.ForeignKey(VDF, null=True, blank=True)
    pcf = models.ForeignKey(PCF, null=True, blank=True)
    active = models.IntegerField(max_length=1, null=False, blank=False, default=1)

class City(models.Model):
    city_name = models.CharField(max_length=20)

class State(models.Model):
    state_name = models.CharField(max_length=20)

class RetryCar(models.Model):
    vin_code = models.CharField(max_length=17, default='')

class Engine_size(models.Model):
    name = models.CharField(max_length=10, null=False, blank=False)

class Pcf_body(models.Model):
    name = models.TextField()
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)