#!/bin/bash

. /home/thomas/devel/virtenv/etoxws-v2/bin/activate


PYTHONPATH=../src python gen_schema_docs.py

make html
make latexpdf