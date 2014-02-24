from django.conf.urls import patterns, include, url


urlpatterns = patterns('etoxwsapi.v1.views',
	url(r'info$', 'info'),
	url(r'dir$', 'available_services'),
	url(r'calculate$', 'calculate'),
)
