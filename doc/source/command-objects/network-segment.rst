===============
network segment
===============

A **network segment** is an isolated Layer 2 segment within a network.
A network may contain multiple network segments. Depending on the
network configuration, Layer 2 connectivity between network segments
within a network may not be guaranteed.

Network v2

network segment list
--------------------

List network segments

.. caution:: This is a beta command and subject to change.
             Use global option ``--os-beta-command`` to
             enable this command.

.. program:: network segment list
.. code:: bash

    os network segment list
        [--long]
        [--network <network>]

.. option:: --long

    List additional fields in output

.. option:: --network <network>

    List network segments that belong to this network (name or ID)

network segment show
--------------------

Display network segment details

.. caution:: This is a beta command and subject to change.
             Use global option ``--os-beta-command`` to
             enable this command.

.. program:: network segment show
.. code:: bash

    os network segment show
        <network-segment>

.. _network_segment_show-segment:
.. describe:: <network-segment>

    Network segment to display (ID only)
