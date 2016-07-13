from django.conf.urls import patterns, include, url

from etoxwsapi.v3.jobs import urls as jobs_urls
from etoxwsapi.v3.schema import _urls as schema_urls

urlpatterns = patterns('etoxwsapi.v3',
	url(r'^/info$', 'views.info', name="v3_info"),
    url(r'^/dir$',  'views.dir', name="v3_dir"),
    url(r'^/pmmdinfo$',  'views.pmmdinfo', name="v3_pmmdinfo"),
    url(r'^/jobs$', 'views.gen_404'),
	url(r'^/jobs/', include(jobs_urls)),
	url(r'^/schema/', include(schema_urls)),
)
