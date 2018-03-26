from django.conf.urls import include, url
from django.conf import settings
from django.views.generic import TemplateView

from rest_framework.authtoken import views as rest_framework_views
from api.api import LoginView
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


# class SimpleStaticView(TemplateView):
#     def get_template_names(self):
#         return [self.kwargs.get('template_name') + ".html"]
#
#     def get(self, request, *args, **kwargs):
#         from django.contrib.auth import authenticate, login
#         if request.user.is_anonymous():
#             # Auto-login the User for Demonstration Purposes
#             user = authenticate()
#             login(request, user)
#         return super(SimpleStaticView, self).get(request, *args, **kwargs)


urlpatterns = [
    url(r'^api/', include('pfinder.api.urls')),
    url(r'^api/api-token-auth/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^(?P<template_name>\w+)$', SimpleStaticView.as_view(), name='pfinder'),

    url(r'^$', TemplateView.as_view(template_name='index.html')),
]

if settings.DEBUG:
    from django.views.static import serve
    import debug_toolbar
    urlpatterns += [
        url(r'^(?P<path>favicon\..*)$', serve, {'document_root': settings.STATIC_ROOT}),
        url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], serve, {'document_root': settings.MEDIA_ROOT}),
        url(r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:], serve, dict(insecure=True)),
        url(r'^__debug__/', include(debug_toolbar.urls))
    ]
