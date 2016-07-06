========
ip fixed
========

Compute v2

ip fixed add
------------

Add fixed IP address to server
(Deprecated, please use ``server add fixed ip`` instead)

.. program:: ip fixed add
.. code:: bash

    os ip fixed add
        <network>
        <server>

.. describe:: <network>

    Network to fetch an IP address from (name or ID)

.. describe:: <server>

    Server to receive the IP address (name or ID)

ip fixed remove
---------------

Remove fixed IP address from server
(Deprecated, please use ``server remove fixed ip`` instead)

.. program:: ip fixed remove
.. code:: bash

    os ip fixed remove
        <ip-address>
        <server>

.. describe:: <ip-address>

    IP address to remove from server (name only)

.. describe:: <server>

    Server to remove the IP address from (name or ID)
