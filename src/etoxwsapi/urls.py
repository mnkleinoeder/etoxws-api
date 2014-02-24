from django.conf.urls import patterns, include, url



urlpatterns = patterns('',
	url(r'^etoxwsapi/v1', include('etoxwsapi.v1.urls')),
	url(r'^etoxwsapi/v2', include('etoxwsapi.v2.urls')),

)
