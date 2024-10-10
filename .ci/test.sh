#!/bin/bash

set -e

python3 -c "from PIL import Image"

python3 -bb -m pytest --threads 1 --iterations 1 -v -x -W always --cov PIL --cov Tests --cov-report term --cov-report xml Tests/oss-fuzz/test_fuzzers.py $REVERSE
