#!/bin/bash

command -v tox > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo 'This script requires "tox" to run.'
  echo 'You can install it with "pip install tox".'
  exit 1; 
fi

tox -evenv -- $@
