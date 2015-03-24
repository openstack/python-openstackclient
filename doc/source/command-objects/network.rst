=======
network
=======

Network v2

network create
--------------

Create new network

.. program:: network create
.. code:: bash

    os network create
        [--domain <domain>]
        [--enable | --disable]
        [--project <project>]
        [--share | --no-share]
        <name>

.. option:: --domain <domain>

    Owner's domain (name or ID)"

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --enable

    Enable network (default)

.. option:: --disable

    Disable network

.. option:: --share

    Share the network between projects

.. option:: --no-share

    Do not share the network between projects

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

.. _network_delete-project:
.. describe:: <network>

    Network to delete (name or ID)

network list
------------

List networks

.. program:: network list
.. code:: bash

    os network list
        [--external]
        [--dhcp <dhcp-id>]
        [--long]

.. option:: --external

    List external networks

.. option:: --dhcp <dhcp-id>

    DHCP agent ID

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

.. _network_set-name:
.. describe:: <network>

    Network to modify (name or ID)

network show
------------

Display network details

.. program:: network show
.. code:: bash

    os network show
        <network>

.. _network_show-name:
.. describe:: <network>

    Network to display (name or ID)
