from django.conf.urls import patterns, include, url

from etoxwsapi.v2.jobs import views
from django.views.decorators.csrf import csrf_exempt


urlpatterns = patterns('',
			url(r'^$', csrf_exempt(views.JobsView.as_view()), name='jobs'),
			url(r'(?P<job_id>\w+)$', views.JobHandlerView.as_view(), name='job_handler'),
)
