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
        [--long]

.. _compute-service-list:
.. option:: --host <host>

    List services on specified host (name only)

.. option:: --service <service>

    List only specified service (name only)

.. option:: --long

    List additional fields in output


compute service set
-------------------

Set service command

.. program:: compute service set
.. code:: bash

    os compute service set
        [--enable | --disable]
        [--disable-reason <reason>]
        <host> <service>

.. _compute-service-set:
.. option:: --enable

    Enable service

.. option:: --disable

    Disable service

.. option:: --disable-reason <reason>

    Reason for disabling the service (in quotes). Should be used with --disable option.

.. describe:: <host>

    Name of host

.. describe:: <service>

    Name of service

