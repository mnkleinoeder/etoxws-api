. {{etoxws_virtenv}}/bin/activate

export LD_LIBRARY_PATH={{RDKIT_DIR}}/lib
export PYTHONPATH={{ETOXWS_APPDIR}}/src:/opt/rdkit/lib/python{{python_version}}/site-packages
{% for p in (ETOXWS_IMPL_V1.PYPATH, ETOXWS_IMPL_V2.PYPATH) %}
{% if p|length > 0 %}
export PYTHONPATH=$PYTHONPATH:{{p}}
{% endif %} 
{% endfor %} 
export DJANGO_SETTINGS_MODULE=etoxwsapi.settings

cd src/etoxwsapi

echo run django with "python manage.py <action>"
