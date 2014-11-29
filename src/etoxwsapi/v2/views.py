from django.http import HttpResponse
from django.conf import settings

v2_impl = settings.ETOXWS_IMPL_V2()

def info(request):
    jsondata = v2_impl.info()
    return HttpResponse(jsondata, content_type='application/json')

def dir(request): #@ReservedAssignment
    jsondata = v2_impl.dir()
    return HttpResponse(jsondata, content_type='application/json')

def pmmdinfo(request): #@ReservedAssignment
    jsondata = v2_impl.pmmdinfo()
    return HttpResponse(jsondata, content_type='application/json')
