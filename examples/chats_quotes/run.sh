#!/usr/bin/env bash



echo "Starting" >> output.log

python run_tests.py >> output.txt 2>&1 &
#| tee -a output.log
