#!/bin/bash

DIR=$(dirname $(readlink -f $0))

export PYTHONPATH=$DIR/src

. $DIR/make_env.sh

celery -A etoxwsapi.djcelery worker -c 2 --loglevel=info
