#!/bin/bash

# This is a script that kicks off a series of functional tests against an
# OpenStack cloud. It will attempt to create an instance if one is not
# available. Do not run this script unless you know what you're doing.
# For more information refer to:
# http://docs.openstack.org/developer/python-openstackclient/

# This particular script differs from the normal post_test_hook because
# it installs the master (tip) version of osc-lib, os-client-config
# and openstacksdk, OSCs most important dependencies.

function generate_testr_results {
    if [ -f .testrepository/0 ]; then
        sudo .tox/functional-tips/bin/testr last --subunit > $WORKSPACE/testrepository.subunit
        sudo mv $WORKSPACE/testrepository.subunit $BASE/logs/testrepository.subunit
        sudo .tox/functional-tips/bin/subunit2html $BASE/logs/testrepository.subunit $BASE/logs/testr_results.html
        sudo gzip -9 $BASE/logs/testrepository.subunit
        sudo gzip -9 $BASE/logs/testr_results.html
        sudo chown jenkins:jenkins $BASE/logs/testrepository.subunit.gz $BASE/logs/testr_results.html.gz
        sudo chmod a+r $BASE/logs/testrepository.subunit.gz $BASE/logs/testr_results.html.gz
    fi
}

export OPENSTACKCLIENT_DIR="$BASE/new/python-openstackclient"
sudo chown -R jenkins:stack $OPENSTACKCLIENT_DIR

# Go to the openstackclient dir
cd $OPENSTACKCLIENT_DIR

# Run tests
echo "Running openstackclient functional-tips test suite"
set +e

# Source environment variables to kick things off
source ~stack/devstack/openrc admin admin
echo 'Running tests with:'
env | grep OS

# Preserve env for OS_ credentials
sudo -E -H -u jenkins tox -e functional-tips
EXIT_CODE=$?
set -e

# Collect and parse result
generate_testr_results
exit $EXIT_CODE
