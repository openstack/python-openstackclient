#!/bin/bash

# This is a script that runs ostestr with the openrc OS_ variables sourced.
# Do not run this script unless you know what you're doing.
# For more information refer to:
# https://docs.openstack.org/python-openstackclient/latest/

# Source environment variables to kick things off
if [ -f ~stack/devstack/openrc ] ; then
    source ~stack/devstack/openrc admin admin
fi

echo 'Running tests with:'
env | grep OS

stestr run $*
