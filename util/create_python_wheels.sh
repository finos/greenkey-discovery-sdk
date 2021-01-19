#!/usr/bin/env bash

# creates python wheels for current python version for copying over to internet-disabled machine
vers=$(python3 --version| awk '{print $NF}')
wheel_dir="${vers}_wheels"
python3 -m pip wheel pip -w "$wheel_dir"
python3 -m pip wheel -r requirements.txt -w "$wheel_dir"
tar -cvzf "${wheel_dir}.tar.gz" "$wheel_dir"