from django.conf.urls import patterns, include, url

from etoxwsapi.v2.jobs import urls as jobs_urls
from etoxwsapi.v2.schema import _urls as schema_urls

urlpatterns = patterns('etoxwsapi.v2',
	url(r'/info$', 'views.info', name="v2_info"),
    url(r'/dir$',  'views.dir', name="v2_dir"),
    url(r'/pmmdinfo$',  'views.pmmdinfo', name="v2_pmmdinfo"),
    url(r'/jobs$', 'views.gen_404'),
	url(r'/jobs/', include(jobs_urls)),
	url(r'/schema/', include(schema_urls)),
)
