from django.conf.urls import patterns, include, url

from etoxwsapi.v3 import schema

urlpatterns = schema.urlconf()
