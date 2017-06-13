============
server event
============

Server event is the event record that had been done on a server, include: event
type(create, delete, reboot and so on), event result(success, error), start
time, finish time and so on. These are important information for server
maintains.

Compute v2

server event list
-----------------

List recent events of a server

.. program:: server event list
.. code:: bash

    openstack server event list
        <server>

.. describe:: <server>

    Server to list events (name or ID)

server event show
-----------------

Show server event details

.. program:: server event show
.. code:: bash

    openstack server event show
        <server>
        <request-id>

.. describe:: <server>

    Server to show event details (name or ID)

.. describe:: <request-id>

     Request ID of the event to show (ID only)
