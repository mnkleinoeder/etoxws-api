#!/bin/bash

DIR=$(dirname $(readlink -f $0))

. $DIR/make_env.sh

cd src/etoxwsapi/

python manage.py runserver 0.0.0.0:8000

