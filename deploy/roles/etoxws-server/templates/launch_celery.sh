#!/bin/bash

. {{ETOXWS_APPDIR}}/make_env.sh


celery -A etoxwsapi.djcelery worker -c 2 --loglevel=info