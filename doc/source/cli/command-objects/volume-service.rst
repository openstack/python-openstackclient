==============
volume service
==============

Block Storage v1, v2

volume service list
-------------------

List volume service

.. program:: volume service list
.. code:: bash

    openstack volume service list
        [--host <host>]
        [--service <service>]
        [--long]

.. option:: --host <host>

    List services on specified host (name only)

.. option:: --service <service>

    List only specified service (name only)

.. option:: --long

    List additional fields in output

volume service set
------------------

Set volume service properties

.. program:: volume service set
.. code:: bash

    openstack volume service set
        [--enable | --disable]
        [--disable-reason <reason>]
        <host>
        <service>

.. option:: --enable

    Enable volume service

.. option:: --disable

    Disable volume service

.. option:: --disable-reason <reason>

    Reason for disabling the service
    (should be used with :option:`--disable` option)

.. _volume_service_set-host:
.. describe:: <host>

    Name of host

.. describe:: <service>

    Name of service (Binary name)
