===============
network segment
===============

A **network segment** is an isolated Layer 2 segment within a network.
A network may contain multiple network segments. Depending on the
network configuration, Layer 2 connectivity between network segments
within a network may not be guaranteed.

Network v2

network segment create
----------------------

Create new network segment

.. program:: network segment create
.. code:: bash

    os network segment create
        [--description <description>]
        [--physical-network <physical-network>]
        [--segment <segment>]
        --network <network>
        --network-type <network-type>
        <name>

.. option:: --description <description>

    Network segment description

.. option:: --physical-network <physical-network>

    Physical network name of this network segment

.. option:: --segment <segment>

    Segment identifier for this network segment which is
    based on the network type, VLAN ID for vlan network
    type and tunnel ID for geneve, gre and vxlan network
    types

.. option:: --network <network>

    Network this network segment belongs to (name or ID)

.. option:: --network-type <network-type>

    Network type of this network segment
    (flat, geneve, gre, local, vlan or vxlan)

.. _network_segment_create-name:
.. describe:: <name>

    New network segment name

network segment delete
----------------------

Delete network segment(s)

.. program:: network segment delete
.. code:: bash

    os network segment delete
        <network-segment> [<network-segment> ...]

.. _network_segment_delete-segment:
.. describe:: <network-segment>

    Network segment(s) to delete (name or ID)

network segment list
--------------------

List network segments

.. program:: network segment list
.. code:: bash

    os network segment list
        [--long]
        [--network <network>]

.. option:: --long

    List additional fields in output

.. option:: --network <network>

    List network segments that belong to this network (name or ID)

network segment set
-------------------

Set network segment properties

.. program:: network segment set
.. code:: bash

    os network segment set
        [--description <description>]
        [--name <name>]
        <network-segment>

.. option:: --description <description>

    Set network segment description

.. option:: --name <name>

    Set network segment name

.. _network_segment_set-segment:
.. describe:: <network-segment>

    Network segment to modify (name or ID)

network segment show
--------------------

Display network segment details

.. program:: network segment show
.. code:: bash

    os network segment show
        <network-segment>

.. _network_segment_show-segment:
.. describe:: <network-segment>

    Network segment to display (name or ID)
