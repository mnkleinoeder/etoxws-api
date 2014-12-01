#!/bin/bash

PYTHONPATH=../src python gen_schema_docs.py

make html
make latexpdf
