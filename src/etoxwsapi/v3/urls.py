from django.conf.urls import patterns, include, url

from etoxwsapi.v3.jobs import urls as jobs_urls
from etoxwsapi.v3.meta import urls as meta_urls
from etoxwsapi.v3.schema import _urls as schema_urls
import django

urlpatterns = patterns('etoxwsapi.v3',
    url(r'^jobs$', django.shortcuts.Http404),
	url(r'^jobs/', include(jobs_urls)),
	url(r'^schema/', include(schema_urls)),
	url(r'^', include(meta_urls)),
)
