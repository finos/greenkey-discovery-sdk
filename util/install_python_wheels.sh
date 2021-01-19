#!/usr/bin/env bash
set -eu

if [ $# -le 1 ]; then
    echo -e "\nUsage: $0 directory-containing-wheels\n"
fi
wheeldir=$1

pushd "$wheeldir"
    # upgrade pip first
    python3 -m pip install --user --no-deps pip*.whl
    for wheel in *.whl; do
        python3 -m pip install --user --no-deps "$wheel"
    done
popd