import json
from rest_framework import generics, permissions
from django.db.models import Q
from rest_framework.filters import  SearchFilter, OrderingFilter
from django.conf import settings
from .serializers import UserSerializer, PostSerializer, PhotoSerializer, CarSerializer, SiteSerializer, CitySerializer, StateSerializer, BuildSheetSerializer, BuildSheetOptionsSerializer
from .models import User, Post, Photo, Car, Site, City, State, BSF
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

        if query_title is not None:
            queryset_list = queryset_list.filter(
                Q(listing_title__icontains=query_title)
            ).distinct()

        if query_price is not None:
            price = query_price.split("-")
            try:
                price_from = price[0]
                price_to = price[1]
            except Exception as e:
                price_from = 1000
                price_to = 10000000

            queryset_list = queryset_list.filter(
                Q(price__gt=price_from)
            ).distinct()

            queryset_list = queryset_list.filter(
                Q(price__lt=price_to)
            ).distinct()

        if query_city is not None:
            queryset_list = queryset_list.filter(
                Q(city__icontains=query_city)
            ).distinct()

        if query_state is not None:
            queryset_list = queryset_list.filter(
                Q(state__icontains=query_state)
            ).distinct()

        if query_description is not None:
            queryset_list = queryset_list.filter(
                Q(listing_description__icontains=query_description)
            ).distinct()

        if query_mileage is not None:
            mileage = query_mileage.split("-")

            try:
                mileage_from = mileage[0]
                mileage_to = mileage[1]
            except Exception as e:
                mileage_from = 0
                mileage_to = 198000

            queryset_list = queryset_list.filter(
                Q(mileage__gt=mileage_from)
            ).distinct()

            queryset_list = queryset_list.filter(
                Q(mileage__lt=mileage_to)
            ).distinct()

        if query_year is not None:
            year = query_year.split("-")

            try:
                year_from = year[0]
                year_to = year[1]
            except Exception as e:
                year_from = 1955
                year_to = year[0]

            queryset_list = queryset_list.filter(
                Q(listing_year__gt=year_from)
            ).distinct()


            queryset_list = queryset_list.filter(
                Q(listing_year__lt=year_to)
            ).distinct()

        if query_model is not None:
            queryset_list = queryset_list.filter(
                Q(listing_model__icontains=query_model)
            ).distinct()

        return queryset_list

class CarDetail(generics.ListAPIView):
    model = Car
    serializer_class = CarSerializer
    search_fields= ['listing_title']
    permission_classes = [
        PostAuthorCanEditPermission
    ]
    def get_queryset(self):
        vin = self.kwargs['vin']
        return Car.objects.filter(vin=vin)


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