===========
ip floating
===========

Compute v2, Network v2

ip floating add
---------------

Add floating IP address to server

.. program:: ip floating add
.. code:: bash

    os ip floating add
        <ip-address>
        <server>

.. describe:: <ip-address>

    IP address to add to server (name only)

.. describe:: <server>

    Server to receive the IP address (name or ID)

ip floating create
------------------

Create new floating IP address

.. program:: ip floating create
.. code:: bash

    os ip floating create
        <pool>

.. describe:: <pool>

    Pool to fetch IP address from (name or ID)

ip floating delete
------------------

Delete floating IP

.. program:: ip floating delete
   .. code:: bash

    os ip floating delete <floating-ip>

.. describe:: <floating-ip>

    Floating IP to delete (IP address or ID)

ip floating list
----------------

List floating IP addresses

.. program:: ip floating list
.. code:: bash

    os ip floating list

ip floating remove
------------------

Remove floating IP address from server

.. program:: ip floating remove
.. code:: bash

    os ip floating remove
        <ip-address>
        <server>

.. describe:: <ip-address>

    IP address to remove from server (name only)

.. describe:: <server>

    Server to remove the IP address from (name or ID)

ip floating show
----------------

Display floating IP details

.. program:: ip floating show
   .. code:: bash

    os ip floating show <floating-ip>

.. describe:: <floating-ip>

    Floating IP to display (IP address or ID)
