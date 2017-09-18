from rest_framework import generics, permissions
from django.db.models import Q
from rest_framework.filters import  SearchFilter, OrderingFilter

from .serializers import UserSerializer, PostSerializer, PhotoSerializer, CarSerializer, SiteSerializer, CitySerializer, StateSerializer
from .models import User, Post, Photo, Car, Site, City, State
from .permissions import PostAuthorCanEditPermission
from rest_framework import viewsets
import rest_framework_filters as filters
import django_filters

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
            queryset_list = queryset_list.filter(
                Q(price__icontains=query_price)
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
            queryset_list = queryset_list.filter(
                Q(mileage__icontains=query_mileage)
            ).distinct()

        if query_year is not None:
            queryset_list = queryset_list.filter(
                Q(listing_year__icontains=query_year)
            ).distinct()

        if query_model is not None:
            queryset_list = queryset_list.filter(
                Q(listing_model__icontains=query_model)
            ).distinct()

        return queryset_list

class CarDetail(generics.ListAPIView):
    model = Car
    serializer_class = CarSerializer

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

class StateList(generics.ListAPIView):
    model = State
    queryset = State.objects.all()
    serializer_class = StateSerializer


