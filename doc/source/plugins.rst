=======
Plugins
=======

The OpenStackClient plugin system is designed so that the plugin need only be
properly installed for OSC to find and use it.  It utilizes the
``setuptools`` entry points mechanism to advertise to OSC the
plugin module and supported commands.

Adoption
========

OpenStackClient promises to provide first class support for the following
OpenStack services: Compute, Identity, Image, Storage, Volume and Network.
These services are considered essential to any OpenStack deployment.

Other OpenStack services, such as Orchestration or Telemetry may create an
OpenStackClient plugin. The source code will not be hosted by
OpenStackClient.

The following is a list of projects and their status as an OpenStackClient
plugin.

=============================  ======================================
   project                     notes
=============================  ======================================
python-barbicanclient          n/a
python-ceilometerclient        n/a
python-congressclient          using only OpenStackClient
python-designateclient         n/a
python-heatclient              plans on creating plugins
python-ironicclient            patch in progress (https://review.openstack.org/#/c/171672/)
python-magnumclient            sent note on ML about creating a plugin
python-manilaclient            n/a
python-mistralclient           n/a
python-muranoclient            n/a
python-saharaclient            n/a
python-troveclient             n/a
python-tuskarclient            using OpenStackClient and their own shell
python-zaqarclient             using only OpenStackClient
=============================  ======================================

Implementation
==============

Plugins are discovered by enumerating the entry points
found under :py:mod:`openstack.cli.extension` and initializing the specified
client module.

.. code-block:: ini

    [entry_points]
    openstack.cli.extension =
        oscplugin = oscplugin.client

The client module must define the following top-level variables:

* ``API_NAME`` - A string containing the plugin API name; this is
  the name of the entry point declaring the plugin client module
  (``oscplugin = ...`` in the example above) and the group name for
  the plugin commands (``openstack.oscplugin.v1 =`` in the example below)
* ``API_VERSION_OPTION`` (optional) - If set, the name of the API
  version attribute; this must be a valid Python identifier and
  match the destination set in ``build_option_parser()``.
* ``API_VERSIONS`` - A dict mapping a version string to the client class

The client module must implement the following interface functions:

* ``build_option_parser(parser)`` - Hook to add global options to the parser
* ``make_client(instance)`` - Hook to create the client object

OSC enumerates the plugin commands from the entry points in the usual manner
defined for the API version:

.. code-block:: ini

    openstack.oscplugin.v1 =
        plugin_list = oscplugin.v1.plugin:ListPlugin
        plugin_show = oscplugin.v1.plugin:ShowPlugin

Note that OSC defines the group name as :py:mod:`openstack.<api-name>.v<version>`
so the version should not contain the leading 'v' character.

.. code-block:: python

    DEFAULT_OSCPLUGIN_API_VERSION = '1'

    # Required by the OSC plugin interface
    API_NAME = 'oscplugin'
    API_VERSION_OPTION = 'os_oscplugin_api_version'
    API_VERSIONS = {
        '1': 'oscplugin.v1.client.Client',
    }

    # Required by the OSC plugin interface
    def make_client(instance):
        """Returns a client to the ClientManager

        Called to instantiate the requested client version.  instance has
        any available auth info that may be required to prepare the client.

        :param ClientManager instance: The ClientManager that owns the new client
        """
        plugin_client = utils.get_client_class(
            API_NAME,
            instance._api_version[API_NAME],
            API_VERSIONS)

        client = plugin_client()
        return client

    # Required by the OSC plugin interface
    def build_option_parser(parser):
        """Hook to add global options

        Called from openstackclient.shell.OpenStackShell.__init__()
        after the builtin parser has been initialized.  This is
        where a plugin can add global options such as an API version setting.

        :param argparse.ArgumentParser parser: The parser object that has been
            initialized by OpenStackShell.
        """
        parser.add_argument(
            '--os-oscplugin-api-version',
            metavar='<oscplugin-api-version>',
            default=utils.env(
                'OS_OSCPLUGIN_API_VERSION',
                default=DEFAULT_OSCPLUGIN_API_VERSION),
            help='OSC Plugin API version, default=' +
                 DEFAULT_OSCPLUGIN_API_VERSION +
                 ' (Env: OS_OSCPLUGIN_API_VERSION)')
        return parser
