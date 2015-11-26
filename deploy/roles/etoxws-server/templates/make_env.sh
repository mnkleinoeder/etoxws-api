. {{etoxws_virtenv}}/bin/activate

export LD_LIBRARY_PATH={{RDKIT_DIR}}/lib
pp=""
{% for p in (ETOXWS_IMPL_V1.PYPATH, ETOXWS_IMPL_V2.PYPATH) %}
{% if p|length > 0 %}
pp={{p}}${pp:+:${pp}}
{% endif %} 
{% endfor %} 

export PYTHONPATH=${pp:+${pp}:}{{ETOXWS_APPDIR}}/src:/opt/rdkit/lib/python{{python_version}}/site-packages
{% if ETOXWS_PRODUCTION|bool %}
export DJANGO_SETTINGS_MODULE=etoxwsapi.settings.prod
{% else %}
# load settings for etoxlab
export DJANGO_SETTINGS_MODULE=etoxwsapi.settings.etoxlabdev
{% endif %} 


#echo {{ETOXWS_APPDIR}}/src/etoxwsapi
#echo run django with "python manage.py <action>"
