from django.http import HttpResponse
from django.conf import settings
from django.http.response import Http404

v3_impl = settings.ETOXWS_IMPL_V3()

def info(request):
    jsondata = v3_impl.info()
    return HttpResponse(jsondata, content_type='application/json')

def dir(request): #@ReservedAssignment
    jsondata = v3_impl.dir()
    return HttpResponse(jsondata, content_type='application/json')

def pmmdinfo(request): #@ReservedAssignment
    jsondata = v3_impl.pmmdinfo()
    return HttpResponse(jsondata, content_type='application/json')

def gen_404(request):
    raise Http404()