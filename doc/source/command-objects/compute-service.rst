===============
compute service
===============

Compute v2

compute service delete
----------------------

Delete compute service(s)

.. program:: compute service delete
.. code:: bash

    os compute service delete
        <service> [<service> ...]

.. _compute-service-delete:
.. describe:: <service>

    Compute service(s) to delete (ID only)

compute service list
--------------------

List compute services

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

Set compute service properties

.. program:: compute service set
.. code:: bash

    os compute service set
        [--enable | --disable]
        [--disable-reason <reason>]
        [--up | --down]
        <host> <service>

.. _compute-service-set:
.. option:: --enable

    Enable service

.. option:: --disable

    Disable service

.. option:: --disable-reason <reason>

    Reason for disabling the service (in quotes). Should be used with --disable option.

.. option:: --up

    Force up service

.. option:: --down

    Force down service

.. describe:: <host>

    Name of host

.. describe:: <service>

    Name of service (Binary name)

