#!/bin/bash

DIR=$(dirname $(readlink -f $0))

. $DIR/make_env.sh

celery -A etoxwsapi.djcelery flower --address=127.0.0.1 --port=5555
