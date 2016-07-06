===============
OpenStackClient
===============

.. image:: https://img.shields.io/pypi/v/python-openstackclient.svg
    :target: https://pypi.python.org/pypi/python-openstackclient/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/dm/python-openstackclient.svg
    :target: https://pypi.python.org/pypi/python-openstackclient/
    :alt: Downloads

OpenStackClient (aka OSC) is a command-line client for OpenStack that brings
the command set for Compute, Identity, Image, Object Store and Block Storage
APIs together in a single shell with a uniform command structure.

The primary goal is to provide a unified shell command structure and a common
language to describe operations in OpenStack.

* `PyPi`_ - package installation
* `Online Documentation`_
* `Launchpad project`_ - release management
* `Blueprints`_ - feature specifications
* `Bugs`_ - issue tracking
* `Source`_
* `Developer` - getting started as a developer
* `Contributing` - contributing code
* `Testing` - testing code
* IRC: #openstack-sdks on Freenode (irc.freenode.net)
* License: Apache 2.0

.. _PyPi: https://pypi.python.org/pypi/python-openstackclient
.. _Online Documentation: http://docs.openstack.org/developer/python-openstackclient/
.. _Launchpad project: https://launchpad.net/python-openstackclient
.. _Blueprints: https://blueprints.launchpad.net/python-openstackclient
.. _Bugs: https://bugs.launchpad.net/python-openstackclient
.. _Source: https://git.openstack.org/cgit/openstack/python-openstackclient
.. _Developer: http://docs.openstack.org/project-team-guide/project-setup/python.html
.. _Contributing: http://docs.openstack.org/infra/manual/developers.html
.. _Testing: http://docs.openstack.org/developer/python-openstackclient/developing.html#testing

Getting Started
===============

OpenStack Client can be installed from PyPI using pip::

    pip install python-openstackclient

There are a few variants on getting help.  A list of global options and supported
commands is shown with ``--help``::

   openstack --help

There is also a ``help`` command that can be used to get help text for a specific
command::

    openstack help
    openstack help server create

If you want to make changes to the OpenStackClient for testing and contribution,
make any changes and then run::

    python setup.py develop

or::

    pip install -e .

Configuration
=============

The CLI is configured via environment variables and command-line
options as listed in  http://docs.openstack.org/developer/python-openstackclient/authentication.html.

Authentication using username/password is most commonly used::

   export OS_AUTH_URL=<url-to-openstack-identity>
   export OS_PROJECT_NAME=<project-name>
   export OS_USERNAME=<username>
   export OS_PASSWORD=<password>  # (optional)

The corresponding command-line options look very similar::

   --os-auth-url <url>
   --os-project-name <project-name>
   --os-username <username>
   [--os-password <password>]

If a password is not provided above (in plaintext), you will be interactively
prompted to provide one securely.

Authentication may also be performed using an already-acquired token
and a URL pointing directly to the service API that presumably was acquired
from the Service Catalog::

    export OS_TOKEN=<token>
    export OS_URL=<url-to-openstack-service>

The corresponding command-line options look very similar::

    --os-token <token>
    --os-url <url-to-openstack-service>
