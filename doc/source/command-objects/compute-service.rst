===============
compute service
===============

Compute v2

compute service delete
----------------------

Delete service command

.. program:: compute service delete
.. code:: bash

    os compute service delete
        <service>

.. _compute-service-delete:
.. describe:: <service>

    Compute service to delete (ID only)

compute service list
--------------------

List service command

.. program:: compute service list
.. code:: bash

    os compute service list
        [--host <host>]
        [--service <service>]

.. _compute-service-list:
.. describe:: --host <host>

    Name of host

.. describe:: --service <service>

    Name of service


compute service set
-------------------

Set service command

.. program:: compute service set
.. code:: bash

    os compute service list
        [--enable | --disable]
        <host> <service>

.. _compute-service-set:
.. describe:: --enable

    Enable service

.. describe:: --disable

    Disable service

.. describe:: <host>

    Name of host

.. describe:: <service>

    Name of service

