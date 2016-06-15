===============
ip availability
===============

Network v2

ip availability list
--------------------

List IP availability for network

This command retrieves information about IP availability.
Useful for admins who need a quick way to check the
IP availability for all associated networks.
List specifically returns total IP capacity and the
number of allocated IP addresses from that pool.

.. program:: ip availability list
.. code:: bash

    os ip availability list
        [--ip-version {4,6}]
        [--project <project>]

.. option:: --ip-version {4,6}

    List IP availability of given IP version networks
    (default is 4)

.. option:: --project <project>

    List IP availability of given project
    (name or ID)

ip availability show
--------------------

Show network IP availability details

This command retrieves information about IP availability.
Useful for admins who need a quick way to
check the IP availability and details for a
specific network.

This command will return information about
IP availability for the network as a whole, and
return availability information for each individual
subnet within the network as well.


.. program:: ip availability show
.. code:: bash

    os ip availability show
        <network>

.. _ip_availability_show-network
.. describe:: <network>

    Show IP availability for a specific network (name or ID)
