#!/bin/bash
#set -e

python setup.py test --slowest --testr-args="$*"

