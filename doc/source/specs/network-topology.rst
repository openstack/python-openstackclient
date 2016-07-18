================
network topology
================

A **network topology** shows a topological graph about
devices which connect to the specific network. Also, it
will return availability information for each individual
device within the network as well. One other thing to note
is that it is the intention for OSC to collect data from
existing REST APIs

Network v2

network topology list
---------------------

List network topologies

.. program:: network topology list
.. code:: bash

    os network topology list
        [--project <project>]

.. option:: --project <project>

    List network topologies for given project
    (name or ID)

network topology show
---------------------

Show network topology details

.. program:: network topology show
.. code:: bash

    os network topology show
        <network>

.. _network_topology_show-network
.. describe:: <network>

    Show network topology for a specific network (name or ID)
