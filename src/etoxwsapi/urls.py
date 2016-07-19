from django.conf.urls import patterns, include, url
from django.conf import settings

def _cleanup_url(url):
	#remove leading "/" if any
	while url.startswith("/") :
		url= url[1:]
	#remove trailing "/" if any
	while url.endswith("/") :
		url= url[:-1]
	
	if url  and not url.endswith("/"):
		url+="/"
	
	return url

_base_url = _cleanup_url(settings.BASE_URL)

urlpatterns = patterns('',
	url(r'^%sv1/'%(_base_url), include('etoxwsapi.v1.urls')),
	url(r'^%sv2/'%(_base_url), include('etoxwsapi.v2.urls')),
	url(r'^%sv3/'%(_base_url), include('etoxwsapi.v3.urls')),
)
