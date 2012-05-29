================
OpenStack Client
================

python-openstackclient is a unified command-line client for the OpenStack APIs.  It is
a thin wrapper to the stock python-*client modules that implement the
actual REST API client actions.

This is an implementation of the design goals shown in 
http://wiki.openstack.org/UnifiedCLI.  The primary goal is to provide
a unified shell command structure and a common language to describe
operations in OpenStack.

python-openstackclient is designed to add support for API extensions via a
plugin mechanism

For release management:

 * https://launchpad.net/python-openstackclient

For blueprints and feature specifications:

 * https://blueprints.launchpad.net/python-openstackclient

For issue tracking:

 * https://bugs.launchpad.net/python-openstackclient

Getting Started
===============

We recommend using a virtualenv to install the client. This description
uses `virtualenvwrapper`_ to create the virtualenv. Install the prereqs,
then build the egg, and install the client into the virtualenv::

    mkvirtualenv openstackclient
    pip install -r tools/pip-requires
    python setup.py build
    easy_install dist/python_openstackclient-0.1-py2.7.egg

.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper

If you want to work in development mode, do this instead::

    mkvirtualenv openstackclient
    pip install -r tools/pip-requires
    python setup.py develop

Toxicity tests can be ran simply by running ``run_tests.sh``

The client can be called interactively by simply typing::
   openstack

Alternatively command line parameters can be called non-interactively::
   openstack --help


Configuration
=============

The cli is configured via environment variables and command-line
options as listed in http://wiki.openstack.org/UnifiedCLI/Authentication.

The 'password flow' variation is most commonly used::

   export OS_AUTH_URL=<url-to-openstack-identity>
   export OS_TENANT_NAME=<tenant-name>
   export OS_USERNAME=<user-name>
   export OS_PASSWORD=<password>    # yes, it isn't secure, we'll address it in the future

The corresponding command-line options look very similar::

   --os-auth-url <url>
   --os-tenant-name <tenant-name>
   --os-username <user-name>
   --os-password <password>

The token flow variation for authentication uses an already-aquired token
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
                         (via httplib2)
   --verbose | -v      # Increase verbosity of output. Can be repeated.
   --quiet | -q        # suppress output except warnings and errors
   --help | -h         # show a help message and exit

Building Contributor Documentation
==================================

This documentation is written by contributors, for contributors.

The source is maintained in the ``docs/source`` folder using
`reStructuredText`_ and built by `Sphinx`_

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx.pocoo.org/

* Building Automatically::

    $ ./run_tests.sh --docs

* Building Manually::

    $ export DJANGO_SETTINGS_MODULE=local.local_settings
    $ python doc/generate_autodoc_index.py
    $ sphinx-build -b html docs/source build/sphinx/html

Results are in the `build/sphinx/html` directory

