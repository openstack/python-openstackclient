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
        interface: internal

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
    --os-interface internal

and can be selected on the command line::

    openstack --os-cloud infra server list

Note that multiple regions are listed in the ``rackspace`` entry.  An otherwise
identical configuration is created for each region.  If ``-os-region-name`` is not
specified on the command line, the first region in the list is used by default.

The selection of ``interface`` (as seen above in the ``rackspace`` entry)
is optional.  For this configuration to work, every service for this cloud
instance must already be configured to support this type of interface.

If you are using Identity v3 you need to specify the user and the project
domain name as shown in the example below:

::

    clouds:
      devstack:
        auth:
          auth_url: http://192.168.122.10:35357/
          project_name: demo
          username: demo
          password: 0penstack
          user_domain_name: Default
          project_domain_name: Default
        region_name: RegionOne

clouds-public.yaml
~~~~~~~~~~~~~~~~~~

:file:`clouds-public.yaml` is a configuration file that is intended to contain
public information about clouds that are common across a large number of users.
The idea is that :file:`clouds-public.yaml` could easily be shared among users
to simplify public cloud configuration.

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

Debugging
~~~~~~~~~
You may find the :doc:`configuration show <command-objects/configuration>`
command helpful to debug configuration issues.  It will display your current
configuration.

Logging Settings
----------------

By setting `log_level` or `log_file` in the configuration
:file:`clouds.yaml`, a user may enable additional logging::

    clouds:
      devstack:
        auth:
          auth_url: http://192.168.122.10:35357/
          project_name: demo
          username: demo
          password: 0penstack
        region_name: RegionOne
        operation_log:
          logging: TRUE
          file: /tmp/openstackclient_demo.log
          level: info
      ds-admin:
        auth:
          auth_url: http://192.168.122.10:35357/
          project_name: admin
          username: admin
          password: 0penstack
        region_name: RegionOne
        log_file: /tmp/openstackclient_admin.log
        log_level: debug

:dfn:`log_file`: ``</path/file-name>``
    Full path to logging file.
:dfn:`log_level`: ``error`` | ``info`` | ``debug``
    If log level is not set, ``warning`` will be used.

If log level is ``info``, the following information is recorded:

* cloud name
* user name
* project name
* CLI start time (logging start time)
* CLI end time
* CLI arguments
* CLI return value
* and any ``info`` messages.

If log level is ``debug``, the following information is recorded:

* cloud name
* user name
* project name
* CLI start time (logging start time)
* CLI end time
* CLI arguments
* CLI return value
* API request header/body
* API response header/body
* and any ``debug`` messages.

When a command is executed, these logs are saved every time. Recording the user
operations can help to identify resource changes and provide useful information
for troubleshooting.

If saving the output of a single command use the `--log-file` option instead.

* `--log-file <LOG_FILE>`

The logging level for `--log-file` can be set by using following options.

*  `-v, --verbose`
*  `-q, --quiet`
*  `--debug`

Locale and Language Support
---------------------------

Full support for languages is included as of OpenStackClient 3.0.0. Here are a
few tips to ensure you have a correct configuration.

Verify preferred python encoding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please perform the following to diagnose ensure locale settings are correct.
Run python interactively and print the preferred encoding value, e.g.:

::

  $ python -c "import locale; print locale.getpreferredencoding()"

If the value is ``ascii`` or ``ANSI_X3.4-1968`` or any other equivalent name for
ASCII the problem is in your environment. You most likely do not have your LANG
environment variable set correctly.

Check the LANG environment variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``LANG`` should be of the form: `lang_code`_`[region_code]`.`encoding`.
For example, it may look like: ``en_US.UTF-8``

The critical part here is the `encoding` value of ``UTF-8``. Python will look
up locale information and if it finds an encoding value, it will set the
encoding property of stdin, stdout and stderr to the value found in your
environment, if it's not defined in your environment it defaults to ASCII.

Redirecting output
~~~~~~~~~~~~~~~~~~

The above only occurs if stdin, stdout and stderr are attached to a TTY. If
redirecting data the encoding on these streams will default to the default
encoding which is set in the `site.py` of your Python distribution, which
defaults to ASCII. A workaround for this is to set ``PYTHONIOENCODING`` to UTF8.

::

  $ PYTHONIOENCODING=utf-8

A final note about DevStack
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A common post devstack operation is to source the ``openrc`` file to set up
environment variables. Doing so will unset the default ``LANG`` environment
variable in your terminal, which will cause the preferred python encoding to
be ``ascii``. We recommend either setting these environment variables
independently or using the ``devstack`` or ``devstack-admin`` os-cloud profile.

::

  $ openstack project list --os-cloud devstack-admin
