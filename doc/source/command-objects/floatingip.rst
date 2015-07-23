==========
floatingip
==========

Compute v2

ip floating add
---------------

Add floating-ip to server

.. program:: ip floating add
.. code:: bash

    os ip floating add
        <ip_address>
        <server>

.. describe:: <ip_address>

    IP address to add to server

.. describe:: <server>

    Server to receive the IP address (name or ID)

ip floating create
------------------

Create new floating-ip

.. program:: ip floating create
.. code:: bash

    os ip floating create
        <pool>

.. describe:: <pool>

    Pool to fetch floating IP from

ip floating delete
------------------

Delete a floating-ip

.. program:: ip floating delete
.. code:: bash

    os ip floating delete
        <ip_address>

.. describe:: <ip_address>

    IP address to delete

ip floating list
----------------

List floating-ips

.. program:: ip floating list
.. code:: bash

    os ip floating list

ip floating remove
------------------

Remove floating-ip from server

.. program:: ip floating remove
.. code:: bash

    os ip floating remove
        <ip_address>
        <server>

.. describe:: <ip_address>

    IP address to remove from server

.. describe:: <server>

    Server to remove the IP address from (name or ID)
