#!/usr/bin/env bash

set -eu

# set tag variable
export TAG=${CIRCLE_SHA1:-master}

teardown() {
  rm -f setup_tests.sh
  rm -f run_tests.sh
}

trap teardown INT TERM EXIT

# run setup
mapfile -t setup_steps < <(python3 -c 'import yaml ; print("\n".join(yaml.load(open(".travis.yml"),Loader=yaml.FullLoader)["jobs"]["include"][0]["install"]))')

echo "#/usr/bin/env bash" > setup_tests.sh
echo "set -exu" >> setup_tests.sh
for setup_step in "${setup_steps[@]}"; do
  echo "$setup_step" >> setup_tests.sh
done

bash setup_tests.sh && rm setup_tests.sh

# run tests
mapfile -t tests < <(python3 -c 'import yaml ; print("\n".join(yaml.load(open(".travis.yml"),Loader=yaml.FullLoader)["jobs"]["include"][0]["script"]))')

echo "#/usr/bin/env bash" > run_tests.sh
echo "set -exu" >> run_tests.sh
for test in "${tests[@]}"; do
  echo $test >> run_tests.sh
done

bash run_tests.sh && rm run_tests.sh
