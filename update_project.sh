#!/bin/bash

if [ ! -e deploy/extern/apache/.git ] ; then
	git submodule init
	git submodule update
else
	git submodule foreach git pull origin master
fi

