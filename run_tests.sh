#!/bin/bash

function usage {
  echo "Usage: $0 [OPTION]..."
  echo "Run python-openstackclient's test suite(s)"
  echo ""
  echo "  -p, --pep8               Just run pep8"
  echo "  -h, --help               Print this usage message"
  echo ""
  echo "This script is deprecated and currently retained for compatibility."
  echo 'You can run the full test suite for multiple environments by running "tox".'
  echo 'You can run tests for only python 2.7 by running "tox -e py27", or run only'
  echo 'the pep8 tests with "tox -e pep8".'
  exit
}

command -v tox > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo 'This script requires "tox" to run.'
  echo 'You can install it with "pip install tox".'
  exit 1; 
fi

just_pep8=0

function process_option {
  case "$1" in
    -h|--help) usage;;
    -p|--pep8) let just_pep8=1;;
  esac
}

for arg in "$@"; do
  process_option $arg
done

if [ $just_pep8 -eq 1 ]; then
  exec tox -e pep8
fi

tox -e py27 $toxargs 2>&1 | tee run_tests.err.log  || exit 1
tox_exit_code=${PIPESTATUS[0]}
if [ 0$tox_exit_code -ne 0 ]; then
  exit $tox_exit_code
fi

if [ -z "$toxargs" ]; then
  tox -e pep8
fi
