from django.conf.urls import patterns, include, url

from etoxwsapi.v2.jobs import urls as jobs_urls

urlpatterns = patterns('etoxwsapi.v2',
	url(r'info$', 'views.info', name="v2_info"),
	url(r'dir$',  'views.dir', name="v2_dir"),
	url(r'jobs/', include(jobs_urls)),
)
