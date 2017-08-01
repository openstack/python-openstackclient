#!/usr/bin/env bash

# Client constraint file contains this client version pin that is in conflict
# with installing the client from source. We should replace the version pin in
# the constraints file before applying it for from-source installation.

ZUUL_CLONER=/usr/zuul-env/bin/zuul-cloner
BRANCH_NAME=master
CLIENT_NAME=python-openstackclient
GIT_BASE=${GIT_BASE:-https://git.openstack.org/}

install_project() {
    local project=$1
    local module_name=$2
    local branch=${3:-$BRANCH_NAME}

    set +e
    project_installed=$(echo "import $module_name" | python 2>/dev/null ; echo $?)
    set -e

    if [ $project_installed -eq 0 ]; then
        echo "ALREADY INSTALLED"
        echo "$project already installed; using existing package"
    elif [ -x "$ZUUL_CLONER" ]; then
        echo "ZUUL CLONER"
        # Make this relative to current working directory so that
        # git clean can remove it. We cannot remove the directory directly
        # since it is referenced after $install_cmd -e
        PROJECT_DIR=$VIRTUAL_ENV/src
        mkdir -p $PROJECT_DIR
        pushd $PROJECT_DIR
        $ZUUL_CLONER --cache-dir \
            /opt/git \
            --branch $branch \
            http://git.openstack.org \
            openstack/$project
        cd openstack/$project
        $install_cmd -e .
        popd
    else
        echo "PIP HARDCODE"
        local GIT_REPO="$GIT_BASE/openstack/$project"
        SRC_DIR="$VIRTUAL_ENV/src/openstack/$project"
        git clone --depth 1 --branch $branch $GIT_REPO $SRC_DIR
        $install_cmd -U -e $SRC_DIR
    fi
}

set -e
set -x

CONSTRAINTS_FILE=$1
shift

install_cmd="pip install"
# NOTE(amotoki): Place this in the tox enviroment's log dir so it will get
# published to logs.openstack.org for easy debugging.
localfile="$VIRTUAL_ENV/log/upper-constraints.txt"
if [[ $CONSTRAINTS_FILE != http* ]]; then
    CONSTRAINTS_FILE=file://$CONSTRAINTS_FILE
fi
curl $CONSTRAINTS_FILE -k -o $localfile
install_cmd="$install_cmd -c$localfile"

install_project requirements openstack_requirements

# This is the main purpose of the script: Allow local installation of
# the current repo. It is listed in constraints file and thus any
# install will be constrained and we need to unconstrain it.
edit-constraints $localfile -- $CLIENT_NAME "-e file://$PWD#egg=$CLIENT_NAME"

# NOTE(amotoki): In feature/osc4 branch we install osc-lib feature/osc4 branch,
# we install the git version of ocs-lib explicitly
# and specify it in upper-constraints.txt
edit-constraints $localfile -- osc-lib "-e file://$VIRTUAL_ENV/src/openstack/osc-lib#egg=osc-lib"
install_project osc-lib osc_lib feature/osc4

$install_cmd -U $*
exit $?
