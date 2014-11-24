
try:
    from .djcelery import jobmgr
except Exception, e:
    print e