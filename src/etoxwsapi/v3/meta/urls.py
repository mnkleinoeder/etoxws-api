from django.conf.urls import patterns, url

urlpatterns = patterns('etoxwsapi.v3.meta',
	url(r'^info$', 'views.info', name="v3_info"),
    url(r'^dir$',  'views.dir', name="v3_dir"),
    url(r'^pmmdinfo$',  'views.pmmdinfo', name="v3_pmmdinfo"),
)
