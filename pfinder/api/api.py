import json
from rest_framework import generics, permissions
from django.db.models import Q
import operator
from rest_framework.filters import  SearchFilter, OrderingFilter
from django.conf import settings
from .serializers import UserSerializer, PostSerializer, PhotoSerializer, CarSerializer, SiteSerializer, CitySerializer, StateSerializer, BuildSheetSerializer, BuildSheetOptionsSerializer, PCFModelNumberSerializer
from .models import User, Post, Photo, Car, Site, City, State, BSF, PCF
from .permissions import PostAuthorCanEditPermission
from rest_framework import views, viewsets
import rest_framework_filters as filters
from rest_framework.authentication import SessionAuthentication, BaseAuthentication
from rest_framework.permissions import IsAuthenticated
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

class CarList(generics.ListAPIView):
    model = Car

    serializer_class = CarSerializer
    filter_backends = [SearchFilter]
    search_fields= ['listing_title']
    permission_classes = [
        PostAuthorCanEditPermission
    ]
    #filter_class = TitleFilter
    def get_queryset(self, *args, **kwargs):
        queryset_list = Car.objects.all()
        query_title = self.request.GET.get("title")
        query_price = self.request.GET.get("price")
        query_city = self.request.GET.get("city")
        query_state = self.request.GET.get("state")
        query_description = self.request.GET.get("description")
        query_mileage = self.request.GET.get("mileage")
        query_year = self.request.GET.get("year")
        query_model = self.request.GET.get("model")
        query_longhood = self.request.GET.get("longhood")
        query_widebody = self.request.GET.get("widebody")
        query_pts = self.request.GET.get("pts")
        query_pccb = self.request.GET.get("pccb")
        query_lwb = self.request.GET.get("lwb")
        query_aircooled = self.request.GET.get("aircooled")
        query_auto_trans = self.request.GET.get("auto_trans")
        query_model_number = self.request.GET.get("model_number")

        if query_title not in (None, 'undefined'): queryset_list = queryset_list.filter(Q(listing_title__icontains=query_title)).distinct()

        if query_price not in (None, 'undefined'):
            price = query_price.split("-")
            try:
                price_from = price[0]
                price_to = price[1]
            except Exception as e:
                price_from = 1000
                price_to = 10000000

            queryset_list = queryset_list.filter(Q(price__gt=price_from)).distinct()

            queryset_list = queryset_list.filter(Q(price__lt=price_to)).distinct()

        if query_city not in ('', 'None', 'undefined', None): queryset_list = queryset_list.filter(Q(city__icontains=query_city)).distinct()

        if query_state not in ('', 'None', 'undefined', None): queryset_list = queryset_list.filter(Q(state__icontains=query_state)).distinct()

        if query_description not in (None, 'undefined', None): queryset_list = queryset_list.filter(Q(listing_description__icontains=query_description)).distinct()

        if query_mileage not in (None, 'undefined', None):
            mileage = query_mileage.split("-")

            try:
                mileage_from = mileage[0]
                mileage_to = mileage[1]
            except Exception as e:
                mileage_from = 0
                mileage_to = 198000

            queryset_list = queryset_list.filter(Q(mileage__gt=mileage_from)).distinct()

            queryset_list = queryset_list.filter(Q(mileage__lt=mileage_to)).distinct()

        if query_year not in (None, 'undefined'):
            year = query_year.split("-")

            try:
                year_from = year[0]
                year_to = year[1]
            except Exception as e:
                year_from = 1955
                year_to = year[0]

            queryset_list = queryset_list.filter(Q(listing_year__gt=year_from)).distinct()

            queryset_list = queryset_list.filter(Q(listing_year__lt=year_to)).distinct()

        if query_model not in (None, 'undefined'): queryset_list = queryset_list.filter(Q(listing_model__icontains=query_model)).distinct()

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

        try:
            queries = self.request.GET.get('keyword').lower()
        except Exception as e:
            queries = None

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
                elif query == 'turbo':
                    query = 'automatic'
                    words.append(query)
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
                elif query.find('lwb') != -1: queryset_list = queryset_list.filter(Q(pcf__lwb_seats__iexact=1)).distinct()
                elif query.find('cooled') != -1: queryset_list = queryset_list.filter(Q(pcf__air_cooled__iexact=1)).distinct()
                else:
                    #queryset_list = queryset_list.filter(
                    q_list = [
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
                        Q(vin__vin__iexact=query),
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

        return queryset_list

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
        return Car.objects.filter(pcf__vid=vin)


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
        return PCF.objects.values('model_number').distinct()

class BuildSheetView(generics.ListAPIView):

    permission_classes = [
        PostAuthorCanEditPermission
    ]

    def post(self, request, format=None):
        vin = request.POST.get("vin")

        data = self.getBSinfo(vin)
        serializer = BuildSheetSerializer(data = data)
        if serializer.is_valid():
            bsf = serializer.save()
            print(bsf.id)
            for item in data['options']:

                item['bsf'] = int(bsf.id)
            print(data['options'])
            bsf_option_serializer = BuildSheetOptionsSerializer(data = data['options'], many=True)

            if bsf_option_serializer.is_valid():
                bsf_option_serializer.save()

            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

            data['model_year'] = model_year
            data['model'] = model
            data['model_detail'] = model_detail
            data['vin'] = vin


        except Exception as e:
            print('Parsing Error in regular expressions')

        vehicle = bs.find('div', {'class':'vehicle'})
        vehicle_labels = vehicle.findAll('div', {'class':'label'})
        vehicle_values = vehicle.findAll('div', {'class':'value'})

        print('Vehicle')
        for i in range(0, len(vehicle_labels)):
            if vehicle_labels[i].text == 'Division:':
                pass
            elif vehicle_labels[i].text == 'Commission #:':
                pass
            elif vehicle_labels[i].text == 'Prod Month:':
                data['production_month'] = vehicle_values[i].text
            elif vehicle_labels[i].text == 'Price:':
                data['msrp'] = vehicle_values[i].text.replace("$", "").replace(",","")
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
            print(option)

        print(data)
        return data