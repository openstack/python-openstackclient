=============
Configuration
=============

OpenStackClient is primarily configured using command line options and environment
variables.  Most of those settings can also be placed into a configuration file to
simplify managing multiple cloud configurations.

There is a relationship between the global options, environment variables and
keywords used in the configuration files that should make translation between
these three areas simple.

Most global options have a corresponding environment variable that may also be
used to set the value. If both are present, the command-line option takes priority.
The environment variable names are derived from the option name by dropping the
leading dashes (--), converting each embedded dash (-) to an underscore (_), and
converting to upper case.

The keyword names in the configurations files are derived from the global option
names by dropping the ``--os-`` prefix if present.

Global Options
--------------

The :doc:`openstack manpage <man/openstack>` lists all of the global
options recognized by OpenStackClient and the default authentication plugins.

Environment Variables
---------------------

The :doc:`openstack manpage <man/openstack>` also lists all of the
environment variables recognized by OpenStackClient and the default
authentication plugins.

Configuration Files
-------------------

clouds.yaml
~~~~~~~~~~~

:file:`clouds.yaml` is a configuration file that contains everything needed
to connect to one or more clouds.  It may contain private information and
is generally considered private to a user.

OpenStackClient looks for a file called :file:`clouds.yaml` in the following
locations:

* current directory
* :file:`~/.config/openstack`
* :file:`/etc/openstack`

The first file found wins.

The keys match the :program:`openstack` global options but without the
``--os-`` prefix.

::

    clouds:
      devstack:
        auth:
          auth_url: http://192.168.122.10:35357/
          project_name: demo
          username: demo
          password: 0penstack
        region_name: RegionOne
      ds-admin:
        auth:
          auth_url: http://192.168.122.10:35357/
          project_name: admin
          username: admin
          password: 0penstack
        region_name: RegionOne
      infra:
        cloud: rackspace
        auth:
          project_id: 275610
          username: openstack
          password: xyzpdq!lazydog
        region_name: DFW,ORD,IAD

In the above example, the ``auth_url`` for the ``rackspace`` cloud is taken
from :file:`clouds-public.yaml` (see below).

The first two entries are for two of the default users of the same DevStack
cloud.

The third entry is for a Rackspace Cloud Servers account.  It is equivalent
to the following options if the ``rackspace`` entry in :file:`clouds-public.yaml`
(below) is present:

::

    --os-auth-url https://identity.api.rackspacecloud.com/v2.0/
    --os-project-id 275610
    --os-username openstack
    --os-password xyzpdq!lazydog
    --os-region-name DFW

and can be selected on the command line::

    openstack --os-cloud infra server list

Note that multiple regions are listed in the ``rackspace`` entry.  An otherwise
identical configuration is created for each region.  If ``-os-region-name`` is not
specified on the command line, the first region in the list is used by default.

clouds-public.yaml
~~~~~~~~~~~~~~~~~~

:file:`clouds-public.yaml` is a configuration file that is intended to contain
public information about clouds that are common across a large number of users.
The idea is that :file:`clouds-public.yaml` could easily be shared among users
to simplify public could configuration.

Similar to :file:`clouds.yaml`, OpenStackClient looks for
:file:`clouds-public.yaml` in the following locations:

* current directory
* :file:`~/.config/openstack`
* :file:`/etc/openstack`

The first file found wins.

The keys here are referenced in :file:`clouds.yaml` ``cloud`` keys.  Anything
that appears in :file:`clouds.yaml`

::

    public-clouds:
      rackspace:
        auth:
          auth_url: 'https://identity.api.rackspacecloud.com/v2.0/'
