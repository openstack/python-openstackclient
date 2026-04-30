.. _neutron-cli-migration:

===========================================
Migrating Project Client OSC Plugins to OSC
===========================================

The guide documents the process for migrating project client OSC plugins from
the project client into ``python-openstackclient``. It focuses on neutron client
and clients for special networking services that were previously implemented as
external OSC plugins (e.g., BGP VPN, TaaS, etc.), but it should apply to any
project client's OSC plugin.

Background
==========

Historically, advanced Neutron services provided their CLI commands through
``python-neutronclient`` as OSC plugins. As the old python-xclient libraries
were deprecated and their functionality were moved to python-openstackclient
it was also decided to move these plugins to python-openstackclient, see the
2025 October PTG etherpad:
https://etherpad.opendev.org/p/oct2025-ptg-neutron#L156

These migrated commands become part of the core OSC codebase but are
organized in separate subdirectories under ``openstackclient/network/v2/``
to maintain clear separation and ownership.

Migration Steps
===============

1. Create the Command Module Directory
---------------------------------------

Create a new python module under ``openstackclient/network/v2/`` for your
service with appropriate name, for example for tap-as-a-service ``taas``.

2. Migrate the Command Classes
-------------------------------

Copy or migrate your command implementation files from the neutronclient
plugin to the new directory. Each command should inherit from the appropriate
base class (i.e.: ``command.Command``, ``command.Lister``, or
``command.ShowOne``).

3. Register Entry Points in pyproject.toml
-------------------------------------------

Add entry points for your commands in ``pyproject.toml`` under a dedicated
group. The group name should be the same as the module name under
``network/v2``.

Example for BGP VPN:

.. code-block:: toml

    [project.entry-points."openstack.network.v2.bgpvpn"]
    bgpvpn_create = "openstackclient.network.v2.bgpvpn.bgpvpn:CreateBgpvpn"
    bgpvpn_delete = "openstackclient.network.v2.bgpvpn.bgpvpn:DeleteBgpvpn"
    bgpvpn_list = "openstackclient.network.v2.bgpvpn.bgpvpn:ListBgpvpn"
    bgpvpn_show = "openstackclient.network.v2.bgpvpn.bgpvpn:ShowBgpvpn"
    bgpvpn_set = "openstackclient.network.v2.bgpvpn.bgpvpn:SetBgpvpn"
    bgpvpn_unset = "openstackclient.network.v2.bgpvpn.bgpvpn:UnsetBgpvpn"

4. Register the Service in API_EXTENSIONS
------------------------------------------

Add your service name to the ``API_EXTENSIONS`` tuple in
``openstackclient/network/client.py``:

.. code-block:: python

    API_EXTENSIONS = ('taas', 'bgpvpn', '<your_service>')

This tells OSC to load the entry points from your dedicated group.

5. Ignore the Old Neutronclient Plugin
---------------------------------------

To prevent conflicts with the old neutronclient plugin (if users still have
it installed), add the old plugin module to the ``IGNORED_MODULES`` tuple in
``openstackclient/shell.py``:

.. code-block:: python

    IGNORED_MODULES = (
        'neutron_taas.taas_client.osc',
        'neutronclient.osc.v2.taas',
        'neutronclient.osc.v2.networking_bgpvpn',
        'neutronclient.osc.v2.<your_old_plugin>',
    )

6. Add Unit Tests
-----------------

Create unit tests under ``openstackclient/tests/unit/network/v2/<service_name>/``.
