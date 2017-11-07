from django.conf.urls import url, include

from .api import UserList, UserDetail
from .api import PostList, PostDetail, UserPostList
from .api import PhotoList, PhotoDetail, PostPhotoList, CarList, CarDetail, ActiveCarDetail, InactiveCarDetail, SiteList, CityList, StateList, BuildSheetView, SearchView, VincodesView

user_urls = [
    url(r'^/(?P<username>[0-9a-zA-Z_-]+)/posts$', UserPostList.as_view(), name='userpost-list'),
    url(r'^/(?P<username>[0-9a-zA-Z_-]+)$', UserDetail.as_view(), name='user-detail'),
    url(r'^$', UserList.as_view(), name='user-list')
]

post_urls = [
    url(r'^/(?P<pk>\d+)/photos$', PostPhotoList.as_view(), name='postphoto-list'),
    url(r'^/(?P<pk>\d+)$', PostDetail.as_view(), name='post-detail'),
    url(r'^$', PostList.as_view(), name='post-list')
]

cars_urls = [
    url(r'^/(?P<vid>.+)/$', CarDetail.as_view(), name='car-detail'),
    url(r'^$', CarList.as_view(), name='car-list')
]

active_urls = [
    url(r'^/(?P<vid>.+)/$', ActiveCarDetail.as_view(), name='car-detail'),
    url(r'^$', CarList.as_view(), name='car-list')
]
inactive_urls = [
    url(r'^/(?P<vid>.+)/$', InactiveCarDetail.as_view(), name='car-detail'),
    url(r'^$', CarList.as_view(), name='car-list')
]

sites_urls = [
    url(r'^$', SiteList.as_view(), name='site-list')
]

cities_urls = [
    url(r'^$', CityList.as_view(), name='city-list')
]

states_urls = [
    url(r'^$', StateList.as_view(), name='state-list')
]
photo_urls = [
    url(r'^/(?P<pk>\d+)$', PhotoDetail.as_view(), name='photo-detail'),
    url(r'^$', PhotoList.as_view(), name='photo-list')
]

bsf_urls = [
    url(r'^$', BuildSheetView.as_view(), name='bsf-detail')
]

search_urls = [
    url(r'^$', SearchView.as_view(), name='search')
]

pcf_urls = [
    url(r'^$', VincodesView.as_view(), name='vincodes')
]
urlpatterns = [
    url(r'^users', include(user_urls)),
    url(r'^posts', include(post_urls)),
    url(r'^photos', include(photo_urls)),
    url(r'^cars', include(cars_urls)),
    url(r'^sites', include(sites_urls)),
    url(r'^cities', include(cities_urls)),
    url(r'^states', include(states_urls)),
    url(r'^bsf', include(bsf_urls)),
    url(r'^search', include(search_urls)),
    url(r'^codes', include(pcf_urls)),
    url(r'^active', include(active_urls)),
    url(r'^inactive', include(inactive_urls)),
]
