from django.conf.urls import patterns, url

from etoxwsapi.v3.jobs_v3 import views
from django.views.decorators.csrf import csrf_exempt


urlpatterns = patterns('',
			url(r'^$', csrf_exempt(views.JobsView.as_view()), name='v3_jobs'),
			url(r'^(?P<job_id>[-\w]+)$', views.JobHandlerView.as_view(), name='v3_job_handler'),
)
