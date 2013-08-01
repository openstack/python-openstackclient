=========
:program:`openstack`
=========


SYNOPSIS
========

:program:`openstack` [<global-options>] <command> [<command-arguments>]

:program:`openstack help` <command>



DESCRIPTION
===========

:program:`openstack` provides a common command-line interface to OpenStack APIs.  It is generally
equivalent to the CLIs provided by the OpenStack project client librariess, but with
a distinct and consistent command structure.

:program:`openstack` uses a similar authentication scheme as the OpenStack project CLIs, with
the credential information supplied either as environment variables or as options on the
command line.  The primary difference is a preference for using
``OS_PROJECT_NAME``/``OS_PROJECT_ID`` over the old tenant-based names.  The old names work
for now though.

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
    Default domain ID (defaults to 'default')


NOTES
=====

[This section intentionally left blank.  So there.]


COMMANDS
========

To get a list of the available commands::

    openstack -h

To get a description of a specific command::

    openstack help <command>


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

The OpenStack project CLIs, the OpenStack API references. <links TBD>
