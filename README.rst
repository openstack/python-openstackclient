================
OpenStack Client
================

OpenStack Client (aka ``python-openstackclient``) is a command-line client for
the OpenStack APIs.
It is primarily a wrapper to the stock python-\*client modules that implement the
actual REST API client actions.

This is an implementation of the design goals shown in
`OpenStack Client Wiki`_.  The primary goal is to provide
a unified shell command structure and a common language to describe
operations in OpenStack.  The master repository is on GitHub_.

.. _OpenStack Client Wiki: https://wiki.openstack.org/wiki/OpenStackClient
.. _GitHub: https://github.com/openstack/python-openstackclient

OpenStack Client has a plugin mechanism to add support for API extensions.

* `Release management`_
* `Blueprints and feature specifications`_
* `Issue tracking`_
* `PyPi`_
* `Developer Docs`_

.. _release management: https://launchpad.net/python-openstackclient
.. _Blueprints and feature specifications: https://blueprints.launchpad.net/python-openstackclient
.. _Issue tracking: https://bugs.launchpad.net/python-openstackclient
.. _PyPi: https://pypi.python.org/pypi/python-openstackclient
.. _Developer Docs: http://docs.openstack.org/developer/python-openstackclient/
.. _install virtualenv: tools/install_venv.py

Note
====

OpenStackClient is considered to be beta release quality as of the 0.3 release;
no assurances are made at this point for ongoing compatibility in command forms
or output.  We do not, however, expect any major changes at this point.

Getting Started
===============

OpenStack Client can be installed from PyPI using pip::

    pip install python-openstackclient

Developers can use the `install virtualenv`_ script to create the virtualenv::

   python tools/install_venv.py
   source .venv/bin/activate
   python setup.py develop

Unit tests are now run using tox.  The ``run_test.sh`` script provides compatibility
but is generally considered deprecated.

The client can be called interactively by simply typing::

   openstack

There are a few variants on getting help.  A list of global options and supported
commands is shown with ``--help``::

   openstack --help

There is also a ``help`` command that can be used to get help text for a specific
command::

    openstack help
    openstack help server create

Configuration
=============

The CLI is configured via environment variables and command-line
options as listed in https://wiki.openstack.org/wiki/OpenStackClient/Authentication.

The 'password flow' variation is most commonly used::

   export OS_AUTH_URL=<url-to-openstack-identity>
   export OS_PROJECT_NAME=<project-name>
   export OS_USERNAME=<user-name>
   export OS_PASSWORD=<password>  # (optional)

The corresponding command-line options look very similar::

   --os-auth-url <url>
   --os-project-name <project-name>
   --os-username <user-name>
   [--os-password <password>]

If a password is not provided above (in plaintext), you will be interactively
prompted to provide one securely.

The token flow variation for authentication uses an already-acquired token
and a URL pointing directly to the service API that presumably was acquired
from the Service Catalog::

    export OS_TOKEN=<token>
    export OS_URL=<url-to-openstack-service>

The corresponding command-line options look very similar::

    --os-token <token>
    --os-url <url-to-openstack-service>

Additional command-line options and their associated environment variables
are listed here::

   --debug             # turns on some debugging of the API conversation
   --verbose | -v      # Increase verbosity of output. Can be repeated.
   --quiet | -q        # suppress output except warnings and errors
   --help | -h         # show a help message and exit

Building Documentation
======================

This documentation is written by contributors, for contributors.

The source is maintained in the ``doc/source`` folder using
`reStructuredText`_ and built by `Sphinx`_

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx.pocoo.org/

Building Manually::

    cd doc
    make html

Results are in the ``build/html`` directory.
