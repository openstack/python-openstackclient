====================
:program:`openstack`
====================

OpenStack Command Line

SYNOPSIS
========

:program:`openstack` [<global-options>] <command> [<command-arguments>]

:program:`openstack help` <command>

:program:`openstack` --help


DESCRIPTION
===========

:program:`openstack` provides a common command-line interface to OpenStack APIs.  It is generally
equivalent to the CLIs provided by the OpenStack project client librariess, but with
a distinct and consistent command structure.

:program:`openstack` uses a similar authentication scheme as the OpenStack project CLIs, with
the credential information supplied either as environment variables or as options on the
command line.  The primary difference is the use of 'project' in the name of the options
``OS_PROJECT_NAME``/``OS_PROJECT_ID`` over the old tenant-based names.

::

    export OS_AUTH_URL=<url-to-openstack-identity>
    export OS_PROJECT_NAME=<project-name>
    export OS_USERNAME=<user-name>
    export OS_PASSWORD=<password>  # (optional)


OPTIONS
=======

:program:`openstack` recognizes the following global topions:

:option:`--os-auth-url <auth-url>`
    Authentication URL

:option:`--os-project-name <auth-project-name>`
    Authentication project name (only one of :option:`--os-project-name` or :option:`--os-project-id` need be supplied)

:option:`--os-project-id <auth-project-id>`
    Authentication tenant ID  (only one of :option:`--os-project-name` or :option:`--os-project-id` need be supplied)

:option:`--os-username <auth-username>`
    Authentication username

:option:`--os-password <auth-password>`
    Authentication password

:option:`--os-region-name <auth-region-name>`
    Authentication region name

:option:`--os-default-domain <auth-domain>`
    Default domain ID (Default: 'default')

:options:`--os-use-keyring`
    Use keyring to store password (default: False)

:option:`--os-cacert <ca-bundle-file>`
    CA certificate bundle file

:option:`--verify|--insecure`
    Verify or ignore server certificate (default: verify)

:option:`--os-identity-api-version <identity-api-version>`
    Identity API version (Default: 2.0)

:option:`--os-XXXX-api-version <XXXX-api-version>`
    Additional API version options will be presend depending on the installed API libraries.


NOTES
=====

[This section intentionally left blank.  So there.]


COMMANDS
========

To get a list of the available commands::

    openstack -h

To get a description of a specific command::

    openstack help <command>


:option:`complete`
    Print the bash completion functions for the current command set.

:option:`help <command>`
    Print help for an individual command


EXAMPLES
========

Show the detailed information for server ``appweb01``::

    openstack --os-tenant-name ExampleCo --os-username demo --os-password secrete --os-auth-url http://localhost:5000:/v2.0 server show appweb01

The same command if the auth environment variables (:envvar:`OS_AUTH_URL`, :envvar:`OS_PROJECT_NAME`,
:envvar:`OS_USERNAME`, :envvar:`OS_PASSWORD`) are set::

    openstack server show appweb01

Create a new image::

    openstack image create \
        --disk-format=qcow2 \
        --container-format=bare \
        --public \
        --copy-from http://somewhere.net/foo.img \
        foo


FILES
=====

  :file:`~/.openstack`


ENVIRONMENT VARIABLES
=====================

The following environment variables can be set to alter the behaviour of :program:`openstack`

:envvar:`OS_USERNAME`
    Set the username

:envvar:`OS_PASSWORD`
    Set the password

:envvar:`OS_PROJECT_NAME`
    Set the project name

:envvar:`OS_AUTH_URL`
    Set the authentication URL


BUGS
====

Bug reports are accepted at the python-openstackclient LaunchPad project
"https://bugs.launchpad.net/python-openstackclient/+bugs".


AUTHORS
=======

Please refer to the AUTHORS file distributed with OpenStackClient.


COPYRIGHT
=========

Copyright 2011-2013 OpenStack Foundation and the authors listed in the AUTHORS file.


LICENSE
=======

http://www.apache.org/licenses/LICENSE-2.0


SEE ALSO
========

The `OpenStackClient page <https://wiki.openstack.org/wiki/OpenStackClient>`_
in the `OpenStack Wiki <https://wiki.openstack.org/>`_ contains further
documentation.

The individual OpenStack project CLIs, the OpenStack API references.
