#!/bin/bash

FUNCTIONAL_TEST_DIR=$(cd $(dirname "$0") && pwd)
source $FUNCTIONAL_TEST_DIR/harpoonrc

OPENSTACKCLIENT_DIR=$FUNCTIONAL_TEST_DIR/..

if [[ -z $DEVSTACK_DIR ]]; then
    DEVSTACK_DIR=$OPENSTACKCLIENT_DIR/../devstack
    if [[ ! -d $DEVSTACK_DIR ]]; then
        DEVSTACK_DIR=$HOME/devstack
        if [[ ! -d $DEVSTACK_DIR ]]; then
            echo "Where did you hide DevStack? Set DEVSTACK_DIR and try again"
            exit 1
        fi
    fi
    echo "Using DevStack found at $DEVSTACK_DIR"
fi

function setup_credentials {
    RC_FILE=$DEVSTACK_DIR/accrc/$HARPOON_USER/$HARPOON_TENANT
    source $RC_FILE
    echo 'sourcing' $RC_FILE
    echo 'running tests with'
    env | grep OS
}

function run_tests {
    cd $FUNCTIONAL_TEST_DIR
    python -m testtools.run discover
    rvalue=$?
    cd $OPENSTACKCLIENT_DIR
    exit $rvalue
}

setup_credentials
run_tests
