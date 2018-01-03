import json
from rest_framework import generics, permissions
from django.db.models import Q
import operator
from rest_framework.filters import  SearchFilter, OrderingFilter
from django.conf import settings
from .serializers import UserSerializer, PostSerializer, PhotoSerializer, CarSerializer, SiteSerializer, CitySerializer, \
    StateSerializer, BuildSheetSerializer, BuildSheetOptionsSerializer, PCFModelNumberSerializer, EngineSizeSearializer, PCFSerializer, PCFBodySerializer
from .models import User, Post, Photo, Car, Site, City, State, BSF, PCF, Engine_size, Pcf_body
from .permissions import PostAuthorCanEditPermission
from rest_framework import views, viewsets
import rest_framework_filters as filters
from rest_framework.authentication import SessionAuthentication, BaseAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
import django_filters
from bs4 import BeautifulSoup
import requests
import re
from decimal import Decimal
from .serializers import SearchSerializer
from itertools import chain
from django.core.mail import send_mail
import datetime, random
import json

class UserMixin(object):
    model = User
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserList(UserMixin, generics.ListAPIView):
    permission_classes = [
        permissions.AllowAny
    ]


class UserDetail(UserMixin, generics.RetrieveAPIView):
    lookup_field = 'username'


class PostMixin(object):
    model = Post
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [
        PostAuthorCanEditPermission
    ]

    def perform_create(self, serializer):
        """Force author to the current user on save"""
        serializer.save(author=self.request.user)


class PostList(PostMixin, generics.ListCreateAPIView):
    pass


class PostDetail(PostMixin, generics.RetrieveUpdateDestroyAPIView):
    pass


class UserPostList(generics.ListAPIView):
    model = Post
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = super(UserPostList, self).get_queryset()
        return queryset.filter(author__username=self.kwargs.get('username'))


class PhotoMixin(object):
    model = Photo
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer


class PhotoList(PhotoMixin, generics.ListCreateAPIView):
    permission_classes = [
        permissions.AllowAny
    ]

class SiteList(generics.ListAPIView):
    model = Site
    queryset = Site.objects.all()
    serializer_class = SiteSerializer

class TitleFilter(django_filters.FilterSet):
    class Meta:
        model = Car
        fields = ['listing_title']

class StandardResultSetPagination(PageNumberPagination):
    page_size = 11
    page_size_query_param = 'page_size'
    max_page_size = 1000
class CarList(generics.ListAPIView):
    model = Car

    serializer_class = CarSerializer
    pagination_class = StandardResultSetPagination
    filter_backends = [SearchFilter]
    search_fields= ['listing_title']
    permission_classes = [
        PostAuthorCanEditPermission
    ]
    #filter_class = TitleFilter
    def get_queryset(self, *args, **kwargs):
        #queryset_list = Car.objects.all()

        queryset_list = Car.objects.select_related('pcf', 'site', 'vin','vdf', 'vhf').all()

        query_title = self.request.GET.get("title")
        listing_exterior_color = self.request.GET.get('listing_exterior_color')
        listing_interior_color = self.request.GET.get('listing_interior_color')
        vin = self.request.GET.get('vin')
        listing_date_start = self.request.GET.get("listing_date_start")
        listing_date_end = self.request.GET.get("listing_date_end")
        listing_transmission = self.request.GET.get('listing_transmission')
        listing_engine_size = self.request.GET.get('listing_engine_size')
        listing_body_type = self.request.GET.get('listing_body_type')
        listing_drivetrain = self.request.GET.get('listing_drivetrain')
        cond = self.request.GET.get('cond')
        seller_type = self.request.GET.get('seller_type')
        pcf_msrp_from = self.request.GET.get("pcf_msrp_from")
        pcf_msrp_to = self.request.GET.get("pcf_msrp_to")

        #query_price = self.request.GET.get("price")
        price_from = self.request.GET.get("price_from")
        price_to = self.request.GET.get("price_to")
        query_city = self.request.GET.get("city")
        query_state = self.request.GET.get("state")
        query_description = self.request.GET.get("description")
        #query_mileage = self.request.GET.get("mileage")
        mileage_from = self.request.GET.get("mileage_from")
        mileage_to = self.request.GET.get("mileage_to")
        #query_year = self.request.GET.get("year")
        year_from = self.request.GET.get("year_from")
        year_to = self.request.GET.get("year_to")
        query_model = self.request.GET.get("model")
        query_longhood = self.request.GET.get("longhood")
        query_widebody = self.request.GET.get("widebody")
        query_pts = self.request.GET.get("pts")
        query_pccb = self.request.GET.get("pccb")
        query_lwb = self.request.GET.get("lwb")
        query_aircooled = self.request.GET.get("aircooled")
        query_auto_trans = self.request.GET.get("auto_trans")
        query_model_number = self.request.GET.get("model_number")

        pcf_id = self.request.GET.get("pcf_id")
        pcf_body_type = self.request.GET.get("pcf_body_type")
        pcf_listing_age_from = self.request.GET.get("pcf_listing_age_from")
        pcf_listing_age_to = self.request.GET.get("pcf_listing_age_to")
        #bsf_msrp_from = self.request.GET.get("bsf_msrp_from")
        bsf_msrp_to = self.request.GET.get("bsf_msrp_to")
        bsf_msrp_from = self.request.GET.get("bsf_msrp_from")
        bsf_model_year_from = self.request.GET.get("bsf_model_year_from")
        bsf_model_year_to = self.request.GET.get("bsf_model_year_to")
        bsf_model_detail = self.request.GET.get("bsf_model_detail")
        bsf_exterior = self.request.GET.get("bsf_exterior")
        bsf_interior = self.request.GET.get("bsf_interior")
        bsf_options = self.request.GET.get('bsf_options')
        bsf_production_month_from = self.request.GET.get("bsf_production_month_from")
        bsf_production_month_to = self.request.GET.get("bsf_production_month_to")
        sold_state = self.request.GET.get('listing_sold_status')

        try:
            sort = self.request.GET.get("sort")
        except Exception as e:
            sort = ''

        try:
            direction = self.request.GET.get("direction")
        except Exception as e:
            direction = ''

        print(sort)
        print(direction)

        if listing_date_start not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(created__gte=listing_date_start)).distinct()
        if listing_date_end not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(created__lte=listing_date_end)).distinct()
        if listing_exterior_color not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(listing_exterior_color__icontains=listing_exterior_color)).distinct()
        if listing_interior_color not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(listing_interior_color__icontains=listing_interior_color)).distinct()
        if vin not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(vin_code__icontains=vin)).distinct()
        if listing_transmission not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(listing_transmission__icontains=listing_transmission)).distinct()
        if listing_engine_size not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(listing_engine_size__icontains=listing_engine_size)).distinct()
        if listing_body_type not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(listing_body_type__icontains=listing_body_type)).distinct()
        if listing_drivetrain not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(listing_drivetrain__icontains=listing_drivetrain)).distinct()
        if sold_state not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(sold_state__iexact=sold_state)).distinct()

        if cond not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(cond__iexact=cond)).distinct()
        if seller_type not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(seller_type__iexact=seller_type)).distinct()

        if query_title not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(listing_title__icontains=query_title)).distinct()

        if price_from not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(price__gt=price_from)).distinct()
        if price_to not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(price__lt=price_to)).distinct()

        if pcf_msrp_from not in ('', 'None', 'undefined', None): queryset_list = queryset_list.filter(Q(pcf__gap_to_msrp__gt=pcf_msrp_from)).distinct()
        if pcf_msrp_to not in ('', 'None', 'undefined', None): queryset_list = queryset_list.filter(Q(pcf__gap_to_msrp__lt=pcf_msrp_to)).distinct()

        if bsf_model_year_from not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(vin__model_year__gt=bsf_model_year_from)).distinct()
        if bsf_model_year_to not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(vin__model_year__lt=bsf_model_year_to)).distinct()

        #queryset_list = queryset_list.filter(Q(pcf__listing_age__gt=pcf_listing_age_from)).distinct()
        #queryset_list = queryset_list.filter(Q(pcf__listing_age__lt=pcf_listing_age_to)).distinct()

        if bsf_msrp_from not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(vin__msrp__gte=bsf_msrp_from)).distinct()
        if bsf_msrp_to not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(vin__msrp__lte=bsf_msrp_to)).distinct()

        if pcf_id not in ('', None, 'undefined'):
            if pcf_id.find('-') > -1:
                pcf_id = pcf_id.split(r"-")
                print(pcf_id)
                pcf_id_value = pcf_id[0] + pcf_id[1]
            else:
                pcf_id_value = pcf_id
            queryset_list = queryset_list.filter(Q(pcf__vid__iexact=pcf_id_value)).distinct()
        if pcf_body_type not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(pcf__body_type__icontains=pcf_body_type)).distinct()
        #if bsf_model_year not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(vin__model_year__iexact=bsf_model_year)).distinct()
        if bsf_model_detail not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(vin__model_detail__icontains=bsf_model_detail)).distinct()
        if bsf_exterior not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(vin__color__icontains=bsf_exterior)).distinct()
        if bsf_interior not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(vin__interior__icontains=bsf_interior)).distinct()
        if bsf_options not in ('', None, 'undefined'):
            q_option_list = [
               Q(vin__options__code__icontains=bsf_options),
               Q(vin__options__value__icontains=bsf_options)
            ]
            queryset_list = queryset_list.filter(reduce(operator.or_, q_option_list)).distinct()

        if bsf_production_month_from not in ('', None, 'undefined'):
            print(int(bsf_production_month_from,10))
            queryset_list = queryset_list.filter(Q(vin__production_month__year__gte=bsf_production_month_from)).distinct()

        if bsf_production_month_to not in ('', None, 'undefined'):
           queryset_list = queryset_list.filter(Q(vin__production_month__year__lte=bsf_production_month_to)).distinct()

        #if bsf_production_month_from not in ('', None, 'undefined') and bsf_production_month_to not in ('', None, 'undefined'):
        #    queryset_list = queryset_list.filter(Q(vin__production_month__range=('01/' + bsf_production_month_from, '01/' + bsf_production_month_to))).distinct()
        #if bsf_production_month_to not in ('', None, 'undefined'): queryset_list = queryset_list.filter(Q(vin__production_month__lt=bsf_production_month_to)).distinct()

        if query_city not in ('', 'None', 'undefined', None): queryset_list = queryset_list.filter(Q(city__icontains=query_city)).distinct()

        if query_state not in ('', 'None', 'undefined', None): queryset_list = queryset_list.filter(Q(state__icontains=query_state)).distinct()

        if query_description not in ('', 'None', 'undefined', None): queryset_list = queryset_list.filter(Q(listing_description__icontains=query_description)).distinct()

        if mileage_from not in ('', 'None', 'undefined', None): queryset_list = queryset_list.filter(Q(mileage__gt=mileage_from)).distinct()
        if mileage_to not in ('', 'None', 'undefined', None): queryset_list = queryset_list.filter(Q(mileage__lt=mileage_to)).distinct()

        if year_from not in ('', 'None', 'undefined', None): queryset_list = queryset_list.filter(Q(listing_year__gt=year_from)).distinct()
        if year_to not in ('', 'None', 'undefined', None): queryset_list = queryset_list.filter(Q(listing_year__lt=year_to)).distinct()

        if query_model not in ('', 'None', None, 'undefined'): queryset_list = queryset_list.filter(Q(listing_model__icontains=query_model)).distinct()

        if query_longhood in ('', 'None', 'undefined', None): pass
        elif query_longhood == 'false': queryset_list = queryset_list.filter(Q(pcf__longhood__iexact=0)).distinct()
        elif query_longhood == 'true': queryset_list = queryset_list.filter(Q(pcf__longhood__iexact=1)).distinct()

        if query_widebody in ('', 'None', 'undefined', None): pass
        elif query_widebody == 'false': queryset_list = queryset_list.filter(Q(pcf__widebody__iexact=0)).distinct()
        elif query_widebody == 'true':  queryset_list = queryset_list.filter(Q(pcf__widebody__iexact=1)).distinct()

        if query_pts in ('', 'None', 'undefined', None): pass
        elif query_pts == 'false': queryset_list = queryset_list.filter(Q(pcf__pts__iexact=0)).distinct()
        elif query_pts == 'true': queryset_list = queryset_list.filter(Q(pcf__pts__iexact=1)).distinct()

        if query_pccb in ('', 'None', 'undefined', None): pass
        elif query_pccb == 'false': queryset_list = queryset_list.filter(Q(pcf__pccb__iexact=0)).distinct()
        elif query_pccb == 'true': queryset_list = queryset_list.filter(Q(pcf__pccb__iexact=1)).distinct()

        if query_lwb in ('', 'None', 'undefined', None): pass
        elif query_lwb == 'false': queryset_list = queryset_list.filter(Q(pcf__lwb_seats__iexact=0)).distinct()
        elif query_lwb == 'true': queryset_list = queryset_list.filter(Q(pcf__lwb_seats__iexact=1)).distinct()

        if query_aircooled in ('', 'None', 'undefined', None): pass
        elif query_aircooled == 'false': queryset_list = queryset_list.filter(Q(pcf__air_cooled__iexact=0)).distinct()
        elif query_aircooled == 'true':  queryset_list = queryset_list.filter(Q(pcf__air_cooled__iexact=1)).distinct()

        if query_auto_trans in ('', 'None', 'undefined', None): pass
        else: queryset_list = queryset_list.filter(Q(pcf__auto_trans__iexact=query_auto_trans)).distinct()

        if query_model_number in ('', 'None', 'undefined', None): pass
        else: queryset_list = queryset_list.filter(Q(pcf__model_number__iexact=query_model_number)).distinct()

        #try:
        queries = self.request.GET.get('keyword').lower()
        if queries.find("-") > -1:
            queries = queries.replace(r"-", '')
        #except Exception as e:
        #    queries = None

        if queries not in (None, 'undefined'):
            words = re.split('; | |, |\*|\n', queries)

            for query in words:
                if query == 'pumpkin':
                    query = 'Orange'
                    words.append(query)
                elif query == 'barney':
                    query = 'Ultraviolet'
                    words.append(query)
                elif query == 'UV':
                    query = 'Ultraviolet'
                    words.append(query)
                elif query == 'gray':
                    query = 'grey'
                    words.append(query)
                elif query == 'stick':
                    query = 'manual'
                    words.append(query)
                elif query == 'auto':
                    query = 'automatic'
                    words.append(query)
                #elif query == 'turbo':
                #    query = 'automatic'
                #    words.append(query)
                elif query == 'long-hood':
                    query = 'long-hood'
                    words.append(query)
                elif query == 'bucket':
                    query = 'lwb'
                    words.append(query)
                elif query == 'wide-body':
                    query = 'widebody'
                    words.append(query)
                elif query == 'paint-to-sample':
                    query = 'pts'
                    words.append(query)
                elif query == 'ceramic':
                    query = 'pccb'
                    words.append(query)
                elif query == 'aircooled':
                    query = 'cooled'
                    words.append(query)
                elif query == 'air-cooled':
                    query = 'cooled'
                    words.append(query)
                elif query == 'bucket':
                    pass
                elif query == 'c2':
                    pass
                elif query == 'c4':
                    pass

                if query.find('longhood') != -1: queryset_list = queryset_list.filter(Q(pcf__longhood__iexact=1)).distinct()
                elif query.find('widebody') != -1: queryset_list = queryset_list.filter(Q(pcf__widebody__iexact=1)).distinct()
                elif query.find('pts') != -1: queryset_list = queryset_list.filter(Q(pcf__pts__iexact=1)).distinct()
                elif query.find('pccb') != -1: queryset_list = queryset_list.filter(Q(pcf__pccb__iexact=1)).distinct()
                elif query.find('cooled') != -1: queryset_list = queryset_list.filter(Q(pcf__air_cooled__iexact=1)).distinct()
                elif query.find('lwb') != -1:
                    q_list = [Q(pcf__lwb_seats__iexact=1), Q(listing_title__icontains='lwb')]
                    queryset_list = queryset_list.filter(reduce(operator.or_, q_list)).distinct()
                elif query.find('cooled') != -1: queryset_list = queryset_list.filter(Q(pcf__air_cooled__iexact=1)).distinct()
                else:
                    #queryset_list = queryset_list.filter(
                    q_list = [
                        Q(vin_code__icontains=query),
                        Q(listing_make__icontains=query),
                        Q(listing_model__icontains=query),
                        Q(listing_model_detail__icontains=query),
                        Q(listing_trim__icontains=query),
                        Q(listing_year__iexact=query),
                        Q(mileage__iexact=query),
                        Q(city__icontains=query),
                        Q(state__iexact=query),
                        Q(listing_year__iexact=query),
                        Q(price__iexact=query),
                        Q(cond__iexact=query),
                        Q(seller_type__iexact=query),
                        Q(listing_exterior_color__iexact=query),
                        Q(listing_interior_color__iexact=query),
                        Q(listing_transmission__iexact=query),
                        Q(listing_transmission_detail__icontains=query),
                        Q(listing_title__icontains=query),
                        Q(listing_engine_size__icontains=query),
                        Q(listing_description__icontains=query),
                        Q(listing_body_type__icontains=query),
                        Q(listing_drivetrain__iexact=query),
                        #Q(listing_drivetrain__iexact=query),
                        Q(vin__msrp__iexact=query),
                        Q(vin__warranty_start__icontains=query),
                        Q(vin__model_year__icontains=query),
                        Q(vin__model_detail__iexact=query),
                        Q(vin__color__iexact=query),
                        Q(vin__production_month__iexact=query),
                        Q(vin__interior__iexact=query),
                        Q(vin__vin__icontains=query),
                        Q(vin__options__value__icontains=query),
                        Q(vin__options__code__icontains=query),
                        Q(pcf__body_type__icontains=query),
                        Q(pcf__model_number__icontains=query),
                        Q(pcf__vid__icontains=query),
                    ]
                    pcf_q_list = [
                        Q(pcf__color__icontains=query),
                        Q(pcf__gap_to_msrp__iexact=query),
                        Q(pcf__listing_age__iexact=query),
                        Q(pcf__auto_trans__icontains=query),
                        Q(pcf__placeholder__iexact=query),
                        Q(pcf__produced_usa__iexact=query),
                        Q(pcf__produced_globally__iexact=query),
                        Q(pcf__same_counts__iexact=query)
                    ]
                    vdf_q_list = [
                        Q(vdf__model_number__icontains=query) |
                        Q(vdf__year__iexact=query) |
                        Q(vdf__model_detail__icontains=query) |
                        Q(vdf__region__icontains=query)
                    ]
                    queryset_list = queryset_list.filter(reduce(operator.or_, q_list)).distinct()
        if sort not in ('', 'None', 'undefined', None):
            print('---------')
            print(direction)
            if direction =='desc':
                queryset_list = queryset_list.order_by('-' + sort)
            elif direction =='asc':
                queryset_list = queryset_list.order_by(sort)

        return queryset_list.filter(pcf__isnull=False)

class CarDetail(generics.ListAPIView):
    model = Car
    serializer_class = CarSerializer
    search_fields= ['listing_title']
    permission_classes = [
        PostAuthorCanEditPermission
    ]
    def get_queryset(self):
        print(self.kwargs)
        vin = self.kwargs['vid']
        queryset_list = Car.objects.filter(pcf__vid=vin)
        #queryset_list = queryset_list.filter(active=1)
        return queryset_list

class ActiveCarDetail(generics.ListAPIView):
    model = Car
    serializer_class = CarSerializer
    search_fields= ['listing_title']
    permission_classes = [
        PostAuthorCanEditPermission
    ]
    def get_queryset(self):
        print(self.kwargs)
        vin = self.kwargs['vid']
        queryset_list = Car.objects.filter(pcf__vid=vin)
        queryset_list = queryset_list.filter(active=1)
        return queryset_list

class InactiveCarDetail(generics.ListAPIView):
    model = Car
    serializer_class = CarSerializer
    search_fields= ['listing_title']
    permission_classes = [
        PostAuthorCanEditPermission
    ]
    def get_queryset(self):
        print(self.kwargs)
        vin = self.kwargs['vid']
        queryset_list = Car.objects.filter(pcf__vid=vin)
        queryset_list = queryset_list.filter(active=0)
        return queryset_list

class PhotoDetail(PhotoMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.AllowAny
    ]


class PostPhotoList(generics.ListAPIView):
    model = Photo
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def get_queryset(self):
        queryset = super(PostPhotoList, self).get_queryset()
        return queryset.filter(post__pk=self.kwargs.get('pk'))

class CityList(generics.ListAPIView):
    model = City
    queryset = City.objects.all()
    serializer_class = CitySerializer
    search_fields= ['listing_title']
    permission_classes = [
        PostAuthorCanEditPermission
    ]

class StateList(generics.ListAPIView):
    model = State
    queryset = State.objects.all()
    serializer_class = StateSerializer
    search_fields= ['listing_title']
    permission_classes = [
        PostAuthorCanEditPermission
    ]

def logout_user(request):
    return render(request, '', {})

def login_form(request):
    return render(request, '', {})
class LoginView(generics.ListAPIView):
    def get_auth_token(request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            if user.is_active:
                token, created = Token.objects.get_or_create(user=user)
                request.session['auth'] = token.key
                return redirect('', request)
        return redirect(settings.LOGIN_URL, request)

class SearchView(generics.ListAPIView):
    model = Car
    serializer_class = CarSerializer
    permission_classes = [
        PostAuthorCanEditPermission
    ]
    def get_queryset(self, *args, **kwargs):
        car = {}
        bsf = {}
        query = self.request.GET.get('keyword').lower()

        cars = Car.objects.all()
        if query is not None:
            if query == 'pumpkin':
                query = 'Orange'
                cars = cars.filter(
                        Q(vin__color__icontains=query)
                    ).distinct()
            elif query == 'barney':
                query = 'Ultraviolet'
                cars = cars.filter(
                        Q(vin__color__icontains=query)
                     ).distinct()
            elif query == 'UV':
                query = 'Ultraviolet'
                bsf = cars.filter(
                        Q(vin__color__icontains=query)
                    ).distinct()
            elif query == 'gray':
                cars = cars.filter(
                        Q(listing_exterior_color__icontains='grey')
                    ).distinct()
            elif query == 'stick':
                cars = cars.filter(
                        Q(listing_transmission__icontains='Manual')
                    ).distinct()
            elif query == 'auto':
                cars = cars.filter(
                        Q(listing_transmission__icontains='Automatic')
                    ).distinct()
            elif query == 'turbo':
                cars = cars.filter(
                        Q(listing_transmission__icontains='Automatic')
                    ).distinct()
            elif query == 'longhood':
                cars = cars.filter(
                        Q(pcf__longhood=1)
                    ).distinct()
            elif query == 'long-hood':
                cars = cars.filter(
                        Q(pcf__longhood=1)
                    ).distinct()
            elif query == 'bucket':
                cars = cars.filter(
                        Q(pcf__lwb_seats=1)
                    ).distinct()
            elif query == 'widebody':
                cars = cars.filter(
                        Q(pcf__widebody=1)
                    ).distinct()
            elif query == 'wide-body':
                cars = cars.filter(
                        Q(pcf__widebody=1)
                    ).distinct()
            elif query == 'pts':
                cars = cars.filter(
                        Q(pcf__pts=1)
                    ).distinct()
            elif query == 'paint-to-sample':
                cars = cars.filter(
                        Q(pcf__pts=1)
                    ).distinct()
            elif query == 'ceramic':
                cars = cars.filter(
                        Q(pcf__pccb=1)
                    ).distinct()
            elif query == 'pccb':
                cars = cars.filter(
                        Q(pcf__pccb=1)
                    ).distinct()
            elif query == 'aircooled':
                cars = cars.filter(
                        Q(pcf__air_cooled=1)
                    ).distinct()
            elif query == 'air-cooled':
                cars = cars.filter(
                        Q(pcf__air_cooled=1)
                    ).distinct()
            elif query == 'bucket':
                pass
            elif query == 'c2':
                pass
            elif query == 'c4':
                pass


        return list(chain(cars, bsf))
class VincodesView(generics.ListAPIView):
    serializer_class = PCFModelNumberSerializer
    permission_classes = [
        PostAuthorCanEditPermission
    ]

    def get_queryset(self):
        return PCF.objects.order_by('model_number').values('model_number').distinct()

class EmailView(generics.ListAPIView):

    permission_classes = [
        permissions.AllowAny
    ]

    def post(self, request, format=None):
        email = request.data.get("email")
        subject = request.data.get("subject")
        content = request.data.get("content")
        print(settings.EMAIL_HOST_USER)
        send_mail('test', content, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False )
        return Response('ok')

class EngineView(generics.ListAPIView):

    queryset = Engine_size.objects.all()
    serializer_class = EngineSizeSearializer
    search_fields = ['name']
    permission_classes = [
        PostAuthorCanEditPermission
    ]

class PcfbodyView(generics.ListAPIView):
    #queryset = Pcf_body.objects.all()
    serializer_class = PCFBodySerializer
    permission_classes = [
        PostAuthorCanEditPermission
    ]
    def get_queryset(self):
        return PCF.objects.values('body_type').distinct()

class BuildSheetView(generics.ListAPIView):
    model = PCF, Site, Car
    permission_classes = [
        PostAuthorCanEditPermission
    ]
    pcf = None

    def post(self, request, format=None):
        vin = request.data.get("id")

        if len(vin) != 17:
            print('return')
            return Response('ok')

        data = Car.objects.filter(vin_code=vin)
        if len(data) > 0:
            car_serializer = CarSerializer(data, many=True)
            return Response({'data':car_serializer.data})

        result = self.parsing_vin(vin)
        data = self.getBSinfo(vin)
        data['model_number'] = result['model_number']
        data['Vin'] = vin
        pcf_data = self.getPCFinfo(data)

        if data['production_month'] != '':
            dt = datetime.datetime.strptime(data['production_month'], '%m/%Y')
            data['production_month'] = dt.date()
        print(data)
        serializer = BuildSheetSerializer(data = data)

        serializer.is_valid()
        print(serializer.errors)

        if serializer.is_valid():
            bGen = False
            while bGen == False:
                newKey = ''.join(random.choice('01234567890ABCDEF') for i in range(6))
                old_results = PCF.objects.filter(vid=newKey)

                if len(old_results) == 0: bGen = True

            newPCFData = {'longhood':pcf_data['longhood'], 'widebody':pcf_data['widebody'], 'pts':pcf_data['pts'], 'pccb':pcf_data['pccb'], 'color':pcf_data['color'], 'body_type':pcf_data['body_type'], 'air_cooled':pcf_data['air_cooled'], 'gap_to_msrp':0, 'listing_age':0, 'lwb_seats':pcf_data['lwb_seats'], 'auto_trans':pcf_data['auto_trans'],
                          'option_code':'', 'option_description':'', 'placeholder':0, 'produced_usa':0, 'produced_globally':0, 'same_counts':0, 'vid':newKey, 'model_number':pcf_data['model_number']}

            pcf_serializer = PCFSerializer(data = newPCFData)
            pcf_serializer.is_valid()
            print(pcf_serializer.errors)

            if pcf_serializer.is_valid():
                new_pcf = pcf_serializer.save()
                print(new_pcf)
                bsf = serializer.save()

                for item in data['options']:
                    item['bsf'] = int(bsf.id)

                bsf_option_serializer = BuildSheetOptionsSerializer(data = data['options'], many=True)

                if bsf_option_serializer.is_valid():
                   bsf_option_serializer.save()

                car = Car(vin_code=vin,
                              listing_make=None,
                              listing_model=None,
                              listing_trim=None,
                              listing_model_detail=bsf.model_detail,
                              listing_year=None,
                              mileage=None,
                              city=None,
                              state=None,
                              listing_date=None,
                              price=None,
                              cond=None,
                              seller_type='',
                              vhr_link='',
                              listing_exterior_color=bsf.color,
                              listing_interior_color=bsf.interior,
                              listing_transmission=None,
                              listing_transmission_detail=None,
                              listing_title=None,
                              listing_url=None,
                              listing_engine_size=None,
                              listing_description='Build Sheet Lookup',
                              sold_state=1,
                              sold_date=None,
                              pcf= new_pcf,
                              vin=bsf,
                              listing_body_type=None,
                              listing_drivetrain=None,
                              created=datetime.datetime.now().date(),
                              updated=datetime.datetime.now().date(),
                              active=0)
                new_car = car.save()
                data = Car.objects.filter(vin_code=bsf.vin)
                car_serializer = CarSerializer(data, many=True)

            return Response({'data':car_serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def getPCFinfo(self, vin_data):
        try:
            year = int(vin_data['model_year'])
        except Exception as e:
            year = 0

        vin = vin_data['Vin']
        #if len(vin) < 17:
        #    return
        bs_option_description = ''
        for option in vin_data['options']:
            bs_option_description = bs_option_description + option['value'] + ','
        try:
            listing_year=0
        except Exception as e:
            listing_year = 0

        listing_title = ''
        listing_transmission = ''
        model_detail = vin_data['model_detail'].lower()

        listing_model_detail = ''
        listing_description = ''
        bs_option_description = bs_option_description.lower()
        listing_color = ''
        #gap_to_msrp = vin_data['gap_to_msrp']

        auto_trans = ''
        longhood = 0
        widebody = 0
        pccb = 0
        pts = 0
        air_cooled = 0
        lwb = 0
        body_type =''

        model_number = vin_data['model_number']

        # if (vin[3] == 'Z') and (vin[4] == 'Z') and (vin[5] == 'Z') : # RoW car
        #     model_number = vin[6] + vin[7] + vin[11]
        # else:
        #     model_number = '9' + vin[7] + vin[11]

        if ((year in (1963, 1973)) or (listing_year in (1963, 1973))) and ((model_detail.find('911') > -1) or (model_detail.find('912') > -1 ) or (listing_model_detail.find('911') > -1) or (listing_model_detail.find('912') > -1 )):
            longhood = 1

        listing_model_detail = listing_model_detail.replace('porsche', '')
        model_detail = model_detail.replace('porsche', '')

        if model_number == '930':
            widebody = 1

        if  (model_number == '964') and ((model_detail.find('turbo') > -1 ) or (listing_model_detail.find('turbo') > -1)):
            widebody = 1

        if  (model_number.find('991') > -1) and ((model_detail.find('turbo') > -1 ) or (listing_model_detail.find('turbo') > -1)):
            widebody = 1

        if  (model_number == '993') and ((model_detail.find('turbo') > -1 ) or (listing_model_detail.find('turbo') > -1)):
            widebody = 1

        if  (model_number == '996') and ((model_detail.find('turbo') > -1 ) or (listing_model_detail.find('turbo') > -1)):
            widebody = 1

        if  (model_number.find('997') > -1 ) and ((model_detail.find('turbo') > -1 ) or (listing_model_detail.find('turbo') > -1)):
            widebody = 1

        if  ((listing_model_detail.find('SSE') > -1) or (model_detail.find('SSE') > -1)  or (listing_description.find('SSE') > -1) or (listing_model_detail.find('super sport equipment') > -1 )
             or (model_detail.find('super sport equipment') > -1) or (listing_description.find('super sport equipment') > -1)) and (listing_year in (1984, 1989) or year in (1984, 1989)):
            widebody = 1
        if (listing_model_detail.find('widebody') > -1 ) or (model_detail.find('widebody') > -1) or (listing_title.find('widebody') > -1) or \
            (listing_model_detail.find('wide body') > -1 ) or (model_detail.find('wide body') > -1) or (listing_title.find('wide body') > -1):
            widebody = 1

        if  (model_number == '964') and ((model_detail.find('anniversary') > -1 ) or (listing_model_detail.find('anniversary') > -1)):
            widebody = 1

        if  (model_number == '993') and ((model_detail.find('2s') > -1 ) or (listing_model_detail.find('4s') > -1)):
            widebody = 1

        if  (model_number.find('997') > -1) and ((model_detail.find(' 4s') > -1 ) or (listing_model_detail.find(' 4s') > -1) or (model_detail.find(' 4') > -1 ) or (listing_model_detail.find(' 4') > -1)):
            widebody = 1

        if  (((model_detail.find('gts') > -1 ) or (listing_model_detail.find('gts') > -1)) and \
            ((model_detail.find('911') > -1 ) or (listing_model_detail.find('911') > -1) or (model_detail.find('carrera') > -1 ) or (listing_model_detail.find('carrera') > -1))):
            widebody = 1

        if  (model_number.find('991') > -1) and ((model_detail.find(' 4') > -1 ) or (listing_model_detail.find(' 4') > -1)):
            widebody = 1

        if  (model_number.find('991') > -1 ) and ((model_detail.find('rs') > -1 ) or (listing_model_detail.find('rs') > -1)):
            widebody = 1


        if (bs_option_description.find('exterior paint to sample') > -1) or (bs_option_description.find('exterior color to sample') > -1) or \
           (listing_title.find(' pts') > -1) or (listing_title.find('paint to sample') > -1) or (listing_title.find('color to sample') > -1) or \
           (listing_description.find(' pts') > -1) or (listing_description.find('paint to sample') > -1) or (listing_description.find('color to sample') > -1):
            pts = 1

        if (bs_option_description.find('ceramic') > -1) or (bs_option_description.find('pccb') > -1) or \
           (listing_title.find('pccb') > -1) or (listing_title.find('ceramic') > -1) or \
           (listing_description.find('pccb') > -1) or (listing_description.find('ceramic') > -1):
            pccb = 1
        if vin not in ('', None):
            if (year in (1948, 1997)) or (listing_year in (1948, 1997)) or (( (year == 1998)or (listing_year == 1998)) and (vin[11] == '3')):
                air_cooled = 1

        if bs_option_description.find('bucket') > -1:
            lwb = 1


        if (listing_transmission == 'auto') and ((listing_year in (1967, 1981)) or (year in (1967, 1981))):
            auto_trans = 'Sportomatic'
        if ((listing_transmission == 'auto'  ) or (bs_option_description.find('tiptronic') > -1)) and ((listing_year in (1989, 2008)) or (year in (1989, 2008))):
            auto_trans = 'Tiptronic'
        if ((listing_transmission == 'auto') or (bs_option_description.find('doppelkupplung') > -1)) and ((listing_year >= 2009) or ( year >= 2009)):
            auto_trans = 'PDK'

        if (listing_model_detail.find('cayenne')>-1) or (model_detail.find('cayenne')>-1):  body_type = 'SUV'
        if (listing_model_detail.find('boxster')>-1) or (model_detail.find('boxster')>-1): body_type = 'Convertible'
        if (listing_model_detail.find('cayman')>-1) or (model_detail.find('cayman')>-1): body_type = 'Coupe'
        if (listing_model_detail.find('panamera')>-1) or (model_detail.find('panamera')>-1): body_type = 'Sedan'
        if (listing_model_detail.find('macan')>-1) or (model_detail.find('macan')>-1): body_type = 'Crossover'
        if (listing_model_detail.find('cabrio')>-1) or (model_detail.find('cabrio')>-1): body_type = 'Convertible'
        if (listing_model_detail.find('cabriolet')>-1) or (model_detail.find('cabriolet')>-1): body_type = 'Convertible'
        if (listing_model_detail.find('coupe')>-1) or (model_detail.find('coupe')>-1): body_type = 'Copue'
        #if (listing_model_detail.find(u'coup', )>-1) or (model_detail.find(u'coup')>-1): body_type = 'Copue'
        if (listing_model_detail.find('roadster')>-1) or (model_detail.find('roadster')>-1): body_type = 'Roadster'
        if (listing_model_detail.find('spyder')>-1) or (model_detail.find('spyder')>-1): body_type = 'Spyder'
        if (listing_model_detail.find('speedster')>-1) or (model_detail.find('speedster')>-1): body_type = 'Convertible'
        if (listing_model_detail.find('targa')>-1) or (model_detail.find('targa')>-1): body_type = 'Targa'
        if (listing_model_detail.find('gt1')>-1) or (model_detail.find('gt1')>-1): body_type = 'Coupe'
        if (listing_model_detail.find('gt2')>-1) or (model_detail.find('gt2')>-1): body_type = 'Coupe'
        if (listing_model_detail.find('gt3')>-1) or (model_detail.find('gt3')>-1): body_type = 'Coupe'
        if (listing_model_detail.find('gt4')>-1) or (model_detail.find('gt4')>-1): body_type = 'Coupe'

        if (listing_model_detail.find(' gt ')>-1) or (model_detail.find(' gt ')>-1): body_type = 'Coupe'

        if (listing_model_detail.find('america')>-1) or (model_detail.find('america')>-1): body_type = 'Coupe'
        if (listing_model_detail.find('cup')>-1) or (model_detail.find('cup')>-1): body_type = 'Coupe'
        if (listing_model_detail.find('914')>-1) or (model_detail.find('914')>-1): body_type = 'Targa'
        if (listing_model_detail.find('924')>-1) or (model_detail.find('924')>-1): body_type = 'Coupe'
        if (listing_model_detail.find('928')>-1) or (model_detail.find('928')>-1): body_type = 'Coupe'
        if (listing_model_detail.find('942')>-1) or (model_detail.find('942')>-1): body_type = 'Coupe'
        if (listing_model_detail.find('gtr')>-1) or (model_detail.find('gtr')>-1): body_type = 'Coupe'

        if (listing_model_detail.find('944')>-1) or (model_detail.find('944')>-1): body_type = 'Coupe'
        if (listing_model_detail.find('911')>-1) or (model_detail.find('911')>-1): body_type = 'Coupe'

        if (listing_model_detail.find('959')>-1) or (model_detail.find('959')>-1): body_type = 'Coupe'

        if (listing_model_detail.find('968')>-1) or (model_detail.find('968')>-1): body_type = 'Coupe'
        if (listing_model_detail.find('912')>-1) or (model_detail.find('912')>-1): body_type = 'Coupe'
        if (listing_model_detail.find('356')>-1) or (model_detail.find('356')>-1): body_type = 'Coupe'

        if (listing_model_detail.find('718')>-1) or (model_detail.find('718')>-1): body_type = 'Coupe'

        color = listing_color


        option_code = ''
        option_description = ''
        placeholder = 0
        producted_usa = 0
        producted_globally = 0
        same_counts = 0
        listing_age = 0

        pcf = {}
        pcf['longhood'] = longhood
        pcf['widebody'] = widebody
        pcf['pts'] = pts
        pcf['pccb'] = pccb
        pcf['color'] = color
        pcf['body_type'] = body_type
        pcf['air_cooled'] = air_cooled
        #pcf['gap_to_msrp'] = gap_to_msrp
        pcf['listing_age'] = 0
        pcf['lwb_seats'] = lwb
        pcf['auto_trans'] = auto_trans
        pcf['option_code'] = ''
        pcf['option_description'] = ''
        pcf['placeholder'] = 0
        pcf['model_number'] = model_number

        return pcf
    def getBSinfo(self, vin):
        data = {}
        url = 'https://admin.porschedealer.com/reports/build_sheets/print.php?vin=%s'

        res = requests.get(url % vin)

        bs = BeautifulSoup(res.content, 'html.parser')
        title = bs.find('h1').text
        try:
            model_year = re.search('(\d{4}\s)(.*?\s)(.*?$)', title).group(1)
            model = re.search('(\d{4}\s)(.*?\s)(.*?$)', title).group(2)
            model_detail =  model + re.search('(\d{4}\s)(.*?\s)(.*?$)', title).group(3)

            data['model_year'] = int(model_year)
            #data['model'] = model
            data['model_detail'] = model_detail
            data['vin'] = vin


        except Exception as e:
            print('Parsing Error in regular expressions')

        vehicle = bs.find('div', {'class':'vehicle'})
        vehicle_labels = vehicle.findAll('div', {'class':'label'})
        vehicle_values = vehicle.findAll('div', {'class':'value'})
        data['warranty_start'] = ''

        for i in range(0, len(vehicle_labels)):
            if vehicle_labels[i].text == 'Division:':
                pass
            elif vehicle_labels[i].text == 'Commission #:':
                pass
            elif vehicle_labels[i].text == 'Prod Month:':
                data['production_month'] = vehicle_values[i].text
            elif vehicle_labels[i].text == 'Price:':
                data['msrp'] = vehicle_values[i].text.replace("$", "").replace(",","")
                if data['msrp']!='':
                    data['msrp'] = int(float(data['msrp']))
                else:
                    data['msrp'] = 0
            elif vehicle_labels[i].text == 'Exterior:':
                data['color'] = vehicle_values[i].text
            elif vehicle_labels[i].text == 'Interior:':
                data['interior'] = vehicle_values[i].text
            elif vehicle_labels[i].text == 'Warranty Start:':
                data['warranty_start'] = vehicle_values[i].text

            print('%s, %s' %(vehicle_labels[i].text, vehicle_values[i].text))

        options = bs.find('div', {'class':'options'})
        options_labels = options.findAll('div', {'class':'label'})
        options_values = options.findAll('div', {'class':'value'})


        data['options'] = []
        for i in range(0, len(options_labels)):
            option = {}
            option['code'] = options_labels[i].text
            option['value'] = options_values[i].text
            data['options'].append(option)
            #print(option)

        return data

    def parsing_vin(self, vin):
        if len(vin) < 17:
            pass
        else:
            model_number = ''
            model_detail = ''
            year = 0

            if (vin[3] == 'Z') and (vin[4] == 'Z') and (vin[5] == 'Z') : # RoW car
                model_number = vin[6] + vin[7] + vin[11]

                if model_number == '911': model_detail = '911 G-model'
                if model_number == '924': model_detail = '924'
                if model_number == '928': model_detail = '928'
                if model_number == '930': model_detail = '930 G-model Turbo'
                if model_number == '931': model_detail = '924 Turbo'
                if model_number == '937': model_detail = '924 Carrera GT'
                if model_number == '944': model_detail = '944'
                if model_number == '951': model_detail = '944 Turbo'
                if model_number == '95B': model_detail = 'Macan'
                if model_number == '964': model_detail = '911 1989-1994'
                if model_number == '968': model_detail = '968'
                if model_number == '970':
                    if vin[9] == '9':
                        model_number = '970.1'
                        model_detail = 'Panamera 2009-2016'
                    elif vin[9] == 'A':
                        model_number = '970.1'
                        model_detail = 'Panamera 2009-2016'
                    elif vin[9] == 'B':
                        model_number = '970.1'
                        model_detail = 'Panamera 2009-2016'
                    elif vin[9] == 'C':
                        model_number = '970.1'
                        model_detail = 'Panamera 2009-2016'
                    elif vin[9] == 'D':
                        model_number = '970.1'
                        model_detail = 'Panamera 2009-2016'
                    elif vin[9] == 'E':
                        model_number = '970.2'
                        model_detail = 'Panamera 2009-2016'
                    elif vin[9] == 'F':
                        model_number = '970.2'
                        model_detail = 'Panamera 2009-2016'
                    elif vin[9] == 'G':
                        model_number = '970.2'
                        model_detail = 'Panamera 2009-2016'

                if model_number == '971': model_detail = 'Panamera 2016-2023'
                if model_number == '980': model_detail = 'Carrera GT'
                if model_number == '981': model_detail = 'Boxster/Cayman 2012-2016'
                if model_number == '982': model_detail = '718 Boxster/Cayman 2016-2019'
                if model_number == '986': model_detail = 'Boxster 1996-2004'
                if model_number == '987':
                    if vin[9] == '5':
                        model_number = '987.1'
                        model_detail = '987 (Boxster/Cayman 2005)'
                    elif vin[9] == '6':
                        model_number = '987.1'
                        model_detail = '987 (Boxster/Cayman 2006)'
                    elif vin[9] == '7':
                        model_number = '987.1'
                        model_detail = '987 (Boxster/Cayman 2007)'
                    elif vin[9] == '8':
                        model_number = '987.1'
                        model_detail = '987 (Boxster/Cayman 2008)'
                    elif vin[9] == '9':
                        model_number = '987.2'
                        model_detail = '987 (Boxster/Cayman 2009)'
                    elif vin[9] == 'A':
                        model_number = '987.2'
                        model_detail = '987 (Boxster/Cayman 2010)'
                    elif vin[9] == 'B':
                        model_number = '987.2'
                        model_detail = '987 (Boxster/Cayman 2011)'
                    elif vin[9] == 'C':
                        model_number = '987.2'
                        model_detail = '987 (Boxster/Cayman 2012)'
                if model_number == '991':
                    if vin[9] == 'C':
                        model_number = '991.1'
                        model_detail = '911 2012'
                    elif vin[9] == 'D':
                        model_number = '991.1'
                        model_detail = '911 2013'
                    elif vin[9] == 'E':
                        model_number = '991.1'
                        model_detail = '911 2014'
                    elif vin[9] == 'F':
                        model_number = '991.1'
                        model_detail = '911 2015'
                    elif vin[9] == 'G':
                        model_number = '991.1'
                        model_detail = '911 2016'
                    elif vin[9] == 'H':
                        model_number = '991.2'
                        model_detail = '911 2017'
                    elif vin[9] == 'J':
                        model_number = '991.2'
                        model_detail = '911 2018'

                if model_number == '993': model_detail = '911 1993-1997'
                if model_number == '996': model_detail = '911 1997-2004'
                if model_number == '997':
                    if vin[9] == '4':
                        model_number = '997.1'
                        model_detail = '991 2004'
                    elif vin[9] == '5':
                        model_number = '997.1'
                        model_detail = '991 2005'
                    elif vin[9] == '6':
                        model_number = '997.1'
                        model_detail = '991 2006'
                    elif vin[9] == '7':
                        model_number = '997.1'
                        model_detail = '991 2007'
                    elif vin[9] == '8':
                        model_number = '997.1'
                        model_detail = '991 2008'
                    elif vin[9] == '9':
                        model_number = '997.2'
                        model_detail = '991 2009'
                    elif vin[9] == 'A':
                        model_number = '997.2'
                        model_detail = '991 2010'
                    elif vin[9] == 'B':
                        model_number = '997.2'
                        model_detail = '991 2011'
                    elif vin[9] == 'C':
                        model_number = '997.2'
                        model_detail = '991 2012'
                    elif vin[9] == 'D':
                        model_number = '997.2'
                        model_detail = '991 2013'

                if model_number == '9PA': model_detail = 'Cayenne 955(2002-2007), 957(2007-2010)'
                if model_number == '92A':
                    model_detail = 'Cayenne 958(2010-2017)'
                    if vin[9] == 'A':
                        model_number = '958.1'
                        model_detail = '958 2010'
                    elif vin[9] == 'B':
                        model_number = '958.1'
                        model_detail = '958 2011'
                    elif vin[9] == 'C':
                        model_number = '958.1'
                        model_detail = '958 2012'
                    elif vin[9] == 'D':
                        model_number = '958.1'
                        model_detail = '958 2013'
                    elif vin[9] == 'E':
                        model_number = '958.1'
                        model_detail = '958 2014'
                    elif vin[9] == 'F':
                        model_number = '958.2'
                        model_detail = '958 2015'
                    elif vin[9] == 'G':
                        model_number = '958.2'
                        model_detail = '958 2016'
                    elif vin[9] == 'H':
                        model_number = '958.2'
                        model_detail = '958 2017'
            else: # US cars
                model_number = vin[7] + vin[11]
                if model_number == '11': model_detail = '911 (G-model)'
                if model_number == '24': model_detail = '924'
                if model_number == '28': model_detail = '928'
                if model_number == '30': model_detail = '930 (911 G-model Turbo)'
                if model_number == '31': model_detail = '924 Turbo'
                if model_number == '44': model_detail = '944'
                if model_number == '51': model_detail = '944 Turbo'
                if model_number == '5B': model_detail = '95B Macan'
                if model_number == '64': model_detail = '964(911 1989-1994)'
                if model_number == '68': model_detail = '968'
                if model_number == '70': model_detail = '970 (Panamera 2009-2016)'
                if model_number == '71': model_detail = '971 (Panamera 2016-2023)'
                if model_number == '80': model_detail = '980 (Carrera GT)'
                if model_number == '81': model_detail = '981 (Boxster/Cayman 2012-2016)'
                if model_number == '82': model_detail = '982 (718 Boxster/Cayman 2016-2019)'
                if model_number == '86': model_detail = '986 (Boxster 1996-2004)'
                if model_number == '87':
                    if vin[9] == '5':
                        model_number = '87.1'
                        model_detail = '987 (Boxster/Cayman 2005)'
                    elif vin[9] == '6':
                        model_number = '87.1'
                        model_detail = '987 (Boxster/Cayman 2006)'
                    elif vin[9] == '7':
                        model_number = '87.1'
                        model_detail = '987 (Boxster/Cayman 2007)'
                    elif vin[9] == '8':
                        model_number = '87.1'
                        model_detail = '987 (Boxster/Cayman 2008)'
                    elif vin[9] == '9':
                        model_number = '87.2'
                        model_detail = '987 (Boxster/Cayman 2009)'
                    elif vin[9] == 'A':
                        model_number = '87.2'
                        model_detail = '987 (Boxster/Cayman 2010)'
                    elif vin[9] == 'B':
                        model_number = '87.2'
                        model_detail = '987 (Boxster/Cayman 2011)'
                    elif vin[9] == 'C':
                        model_number = '87.2'
                        model_detail = '987 (Boxster/Cayman 2012)'
                if model_number == '91':
                    if vin[9] == 'C':
                        model_number = '91.1'
                        model_detail = '911 2012'
                    elif vin[9] == 'D':
                        model_number = '91.1'
                        model_detail = '911 2013'
                    elif vin[9] == 'E':
                        model_number = '91.1'
                        model_detail = '911 2014'
                    elif vin[9] == 'F':
                        model_number = '91.1'
                        model_detail = '911 2015'
                    elif vin[9] == 'G':
                        model_number = '91.1'
                        model_detail = '911 2016'
                    elif vin[9] == 'H':
                        model_number = '91.2'
                        model_detail = '911 2017'
                    elif vin[9] == 'J':
                        model_number = '91.2'
                        model_detail = '911 2018'

                if model_number == '93': model_detail = '993 (911 1993-1997)'
                if model_number == '96': model_detail = '996 (911 1997-2004)'
                if model_number == '97':
                    if vin[9] == '4':
                        model_number = '97.1'
                        model_detail = '991 2004'
                    elif vin[9] == '5':
                        model_number = '97.1'
                        model_detail = '991 2005'
                    elif vin[9] == '6':
                        model_number = '97.1'
                        model_detail = '991 2006'
                    elif vin[9] == '7':
                        model_number = '97.1'
                        model_detail = '991 2007'
                    elif vin[9] == '8':
                        model_number = '97.1'
                        model_detail = '991 2008'
                    elif vin[9] == '9':
                        model_number = '97.2'
                        model_detail = '991 2009'
                    elif vin[9] == 'A':
                        model_number = '97.2'
                        model_detail = '991 2010'
                    elif vin[9] == 'B':
                        model_number = '97.2'
                        model_detail = '991 2011'
                    elif vin[9] == 'C':
                        model_number = '97.2'
                        model_detail = '991 2012'
                    elif vin[9] == 'D':
                        model_number = '97.2'
                        model_detail = '991 2013'

                if model_number == 'PA':
                    model_detail = 'Cayenne 955(2002-2007), 957(2007-2010)'
                    model_number = '55'
                if model_number == '2A':
                    model_detail = 'Cayenne 958(2010-2017)'
                    model_number = '58'

                model_number = '9' + model_number

            year_code = vin[9] #year code

            if year_code == '1': year = 2001
            if year_code == '2': year = 2002
            if year_code == '3': year = 2003
            if year_code == '4': year = 2004
            if year_code == '5': year = 2005
            if year_code == '6': year = 2006
            if year_code == '7': year = 2007
            if year_code == '8': year = 2008
            if year_code == '9': year = 2009
            if year_code == 'A': year = 2010
            if year_code == 'B': year = 2011
            if year_code == 'C': year = 2012
            if year_code == 'D': year = 2013
            if year_code == 'E': year = 2014
            if year_code == 'F': year = 2015
            if year_code == 'G': year = 2016
            if year_code == 'H': year = 2017
            if year_code == 'J': year = 2018
            if year_code == 'K': year = 2019
            if year_code == 'L': year = 2020
            if year_code == 'M': year = 2021
            if year_code == 'N': year = 2022
            if year_code == 'P': year = 2023
            if year_code == 'R': year = 2024
            if year_code == 'S': year = 2025
            if year_code == 'T': year = 2026
            if year_code == 'V': year = 2027
            if year_code == 'W': year = 2028
            if year_code == 'X': year = 2029

            if model_number == '964' or year_code > 2017:
                year = year - 30

            result = {}
            result['model_detail'] = model_detail
            result['model_number'] = model_number
            result['year'] =  year

            return result
