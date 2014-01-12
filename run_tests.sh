#!/bin/bash
#set -e

if [ "$1" = "--coverage" ]; then
        COVERAGE_ARG="$1"
        shift
fi

python setup.py testr --slowest --testr-args="$*" $COVERAGE_ARG

