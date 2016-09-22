=======
network
=======

A **network** is an isolated Layer 2 networking segment. There are two types
of networks, project and provider networks. Project networks are fully isolated
and are not shared with other projects. Provider networks map to existing
physical networks in the data center and provide external network access for
servers and other resources. Only an OpenStack administrator can create
provider networks. Networks can be connected via routers.

Compute v2, Network v2

network create
--------------

Create new network

.. program:: network create
.. code:: bash

    os network create
        [--project <project> [--project-domain <project-domain>]]
        [--enable | --disable]
        [--share | --no-share]
        [--description <description>]
        [--availability-zone-hint <availability-zone>]
        [--enable-port-security | --disable-port-security]
        [--external [--default | --no-default] | --internal]
        [--provider-network-type <provider-network-type>]
        [--provider-physical-network <provider-physical-network>]
        [--provider-segment <provider-segment>]
        [--transparent-vlan | --no-transparent-vlan]
        <name>

.. option:: --project <project>

    Owner's project (name or ID)

    *Network version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    *Network version 2 only*

.. option:: --enable

    Enable network (default)

    *Network version 2 only*

.. option:: --disable

    Disable network

    *Network version 2 only*

.. option:: --share

    Share the network between projects

.. option:: --no-share

    Do not share the network between projects

.. option:: --description <description>

    Set network description

.. option:: --availability-zone-hint <availability-zone>

    Availability Zone in which to create this network
    (Network Availability Zone extension required,
    repeat option to set multiple availability zones)

    *Network version 2 only*

.. option:: --enable-port-security

    Enable port security by default for ports created on
    this network (default)

    *Network version 2 only*

.. option:: --disable-port-security

    Disable port security by default for ports created on
    this network

    *Network version 2 only*

.. option:: --subnet <subnet>

    IPv4 subnet for fixed IPs (in CIDR notation)

    *Compute version 2 only*

.. option:: --external

    Set this network as an external network
    (external-net extension required)

    *Network version 2 only*

.. option:: --internal

    Set this network as an internal network (default)

    *Network version 2 only*

.. option:: --default

    Specify if this network should be used as
    the default external network

    *Network version 2 only*

.. option:: --no-default

    Do not use the network as the default external network
    (default)

    *Network version 2 only*

.. option:: --provider-network-type <provider-network-type>

    The physical mechanism by which the virtual network is implemented.
    The supported options are: flat, geneve, gre, local, vlan, vxlan.

    *Network version 2 only*

.. option:: --provider-physical-network <provider-physical-network>

    Name of the physical network over which the virtual network is implemented

    *Network version 2 only*

.. option:: --provider-segment <provider-segment>

    VLAN ID for VLAN networks or Tunnel ID for GENEVE/GRE/VXLAN networks

    *Network version 2 only*

.. option:: --transparent-vlan

    Make the network VLAN transparent

    *Network version 2 only*

.. option:: --no-transparent-vlan

    Do not make the network VLAN transparent

    *Network version 2 only*

.. _network_create-name:
.. describe:: <name>

    New network name

network delete
--------------

Delete network(s)

.. program:: network delete
.. code:: bash

    os network delete
        <network> [<network> ...]

.. _network_delete-network:
.. describe:: <network>

    Network(s) to delete (name or ID)

network list
------------

List networks

.. program:: network list
.. code:: bash

    os network list
        [--external | --internal]
        [--long]
        [--name <name>]
        [--enable | --disable]
        [--project <project> [--project-domain <project-domain>]]
        [--share | --no-share]
        [--status <status>]

.. option:: --external

    List external networks

.. option:: --internal

    List internal networks

.. option:: --long

    List additional fields in output

.. option:: --name <name>

    List networks according to their name

.. option:: --enable

    List enabled networks

.. option:: --disable

    List disabled networks

.. option:: --project <project>

    List networks according to their project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --share

    List networks shared between projects

.. option:: --no-share

    List networks not shared between projects

.. option:: --status <status>

    List networks according to their status
    ('ACTIVE', 'BUILD', 'DOWN', 'ERROR')

network set
-----------

Set network properties

*Network version 2 only*

.. program:: network set
.. code:: bash

    os network set
        [--name <name>]
        [--enable | --disable]
        [--share | --no-share]
        [--description <description>]
        [--enable-port-security | --disable-port-security]
        [--external [--default | --no-default] | --internal]
        [--provider-network-type <provider-network-type>]
        [--provider-physical-network <provider-physical-network>]
        [--provider-segment <provider-segment>]
        [--transparent-vlan | --no-transparent-vlan]
        <network>

.. option:: --name <name>

    Set network name

.. option:: --enable

    Enable network

.. option:: --disable

    Disable network

.. option:: --share

    Share the network between projects

.. option:: --no-share

    Do not share the network between projects

.. option:: --description <description>

    Set network description

.. option:: --enable-port-security

    Enable port security by default for ports created on
    this network

.. option:: --disable-port-security

    Disable port security by default for ports created on
    this network

.. option:: --external

    Set this network as an external network.
    (external-net extension required)

.. option:: --internal

    Set this network as an internal network

.. option:: --default

    Set the network as the default external network

.. option:: --no-default

    Do not use the network as the default external network.

.. option:: --provider-network-type <provider-network-type>

    The physical mechanism by which the virtual network is implemented.
    The supported options are: flat, gre, local, vlan, vxlan.

.. option:: --provider-physical-network <provider-physical-network>

    Name of the physical network over which the virtual network is implemented

.. option:: --provider-segment <provider-segment>

    VLAN ID for VLAN networks or Tunnel ID for GRE/VXLAN networks

.. option:: --transparent-vlan

    Make the network VLAN transparent

.. option:: --no-transparent-vlan

    Do not make the network VLAN transparent

.. _network_set-network:
.. describe:: <network>

    Network to modify (name or ID)

network show
------------

Display network details

.. program:: network show
.. code:: bash

    os network show
        <network>

.. _network_show-network:
.. describe:: <network>

    Network to display (name or ID)
