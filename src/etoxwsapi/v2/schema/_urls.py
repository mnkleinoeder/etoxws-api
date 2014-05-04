from django.conf.urls import patterns, include, url

from etoxwsapi.v2 import schema

urlpatterns = schema.urlconf()
