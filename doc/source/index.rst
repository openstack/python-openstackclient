===============
OpenStackClient
===============

OpenStackClient (aka OSC) is a command-line client for OpenStack that
brings the command set for Compute, Identity, Image, Object Storage and
Block Storage APIs together in a single shell with a uniform command
structure.

User Documentation
------------------

.. toctree::
   :maxdepth: 1

   Manual Page <man/openstack>
   command-list
   commands
   configuration
   plugins
   plugin-commands
   authentication
   interactive
   humaninterfaceguide
   backwards-incompatible

Getting Started
---------------

* Try :doc:`some commands <command-list>`
* Read the source `on OpenStack's Git server`_
* Install OpenStackClient from `PyPi`_ or a `tarball`_

Release Notes
-------------

.. toctree::
   :maxdepth: 1

   Release Notes <http://docs.openstack.org/releasenotes/python-openstackclient>
   history

Developer Documentation
-----------------------

.. toctree::
   :maxdepth: 1

   developing
   command-beta
   command-options
   command-wrappers
   command-errors
   command-logs
   specs/commands

Project Goals
-------------

* Use the OpenStack Python API libraries, extending or replacing them as required
* Use a consistent naming and structure for commands and arguments
* Provide consistent output formats with optional machine parseable formats
* Use a single-binary approach that also contains an embedded shell that can execute
  multiple commands on a single authentication (see libvirt's virsh for an example)
* Independence from the OpenStack project names; only API names are referenced (to
  the extent possible)

Contributing
============

OpenStackClient utilizes all of the usual OpenStack processes and requirements for
contributions.  The code is hosted `on OpenStack's Git server`_. `Bug reports`_
and `blueprints`_ may be submitted to the :code:`python-openstackclient` project
on `Launchpad`_.  Code may be submitted to the
:code:`openstack/python-openstackclient` project using `Gerrit`_.
Developers may also be found in the `IRC channel`_ ``#openstack-sdks``.

.. _`on OpenStack's Git server`: https://git.openstack.org/cgit/openstack/python-openstackclient/tree
.. _Launchpad: https://launchpad.net/python-openstackclient
.. _Gerrit: http://docs.openstack.org/infra/manual/developers.html#development-workflow
.. _Bug reports: https://bugs.launchpad.net/python-openstackclient/+bugs
.. _blueprints: https://blueprints.launchpad.net/python-openstackclient
.. _PyPi: https://pypi.python.org/pypi/python-openstackclient
.. _tarball: http://tarballs.openstack.org/python-openstackclient
.. _IRC channel: https://wiki.openstack.org/wiki/IRC

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
