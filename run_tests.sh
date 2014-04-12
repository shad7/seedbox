#!/bin/bash
#set -e

python setup.py testr --slowest --testr-args="$*"

