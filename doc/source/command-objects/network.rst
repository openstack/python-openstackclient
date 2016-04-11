=======
network
=======

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
        [--availability-zone-hint <availability-zone>]
        [--external [--default | --no-default] | --internal]
        [--provider-network-type <provider-network-type>]
        [--provider-physical-network <provider-physical-network>]
        [--provider-segment <provider-segment>]
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

.. option:: --availability-zone-hint <availability-zone>

    Availability Zone in which to create this network (requires the Network
    Availability Zone extension, this option can be repeated).

    *Network version 2 only*

.. option:: --subnet <subnet>

    IPv4 subnet for fixed IPs (in CIDR notation)

    *Compute version 2 only*

.. option:: --external

    Set this network as an external network.
    Requires the "external-net" extension to be enabled.

    *Network version 2 only*

.. option:: --internal

    Set this network as an internal network (default)

    *Network version 2 only*

.. option:: --default

    Specify if this network should be used as
    the default external network

    *Network version 2 only*

.. option:: --no-default

    Do not use the network as the default external network.
    By default, no network is set as an external network.

    *Network version 2 only*

.. option:: --provider-network-type <provider-network-type>

    The physical mechanism by which the virtual network is implemented.
    The supported options are: flat, gre, local, vlan, vxlan

    *Network version 2 only*

.. option:: --provider-physical-network <provider-physical-network>

    Name of the physical network over which the virtual network is implemented

    *Network version 2 only*

.. option:: --provider-segment <provider-segment>

    VLAN ID for VLAN networks or Tunnel ID for GRE/VXLAN networks

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
        [--external]
        [--long]

.. option:: --external

    List external networks

.. option:: --long

    List additional fields in output

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
