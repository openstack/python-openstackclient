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
        <name>

.. option:: --project <project>

    Owner's project (name or ID)
    (Network v2 only)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.
    (Network v2 only)

.. option:: --enable

    Enable network (default)
    (Network v2 only)

.. option:: --disable

    Disable network
    (Network v2 only)

.. option:: --share

    Share the network between projects

.. option:: --no-share

    Do not share the network between projects

.. option:: --availability-zone-hint <availability-zone>

    Availability Zone in which to create this network (requires the Network
    Availability Zone extension, this option can be repeated).
    (Network v2 only)

.. option:: --subnet <subnet>

    IPv4 subnet for fixed IPs (in CIDR notation)
    (Compute v2 network only)

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
