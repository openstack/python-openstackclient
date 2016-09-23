=============
network meter
=============

A **network meter** allows operators to measure
traffic for a specific IP range. The following commands
are specific to the L3 metering extension.

Network v2

network meter create
--------------------

Create network meter

.. program:: network meter create
.. code:: bash

    openstack network meter create
        [--project <project> [--project-domain <project-domain>]]
        [--description <description>]
        [--share | --no-share]
        <name>

.. option:: --project <project>

    Owner's project (name of ID)

    *Network version 2 only*

.. option:: --description <description>

    Description of meter

    *Network version 2 only*

.. option:: --share

    Share the meter between projects

.. option:: --no-share

    Do not share the meter between projects (Default)

.. _network_meter_create:
.. describe:: <name>

    New meter name

network meter delete
--------------------

Delete network meter(s)

.. program:: network meter delete
.. code:: bash

    openstack network meter delete
        <meter> [<meter> ...]

.. _network_meter_delete:
.. describe:: <meter>

    Meter(s) to delete (name or ID)

network meter list
------------------

List network meters

.. program:: network meter list
.. code:: bash

    openstack network meter list


network meter show
------------------

Show network meter

.. program:: network meter show
.. code:: bash

    openstack network meter show
        <meter>

.. _network_meter_show:
.. describe:: <meter>

    Meter to display (name or ID)
