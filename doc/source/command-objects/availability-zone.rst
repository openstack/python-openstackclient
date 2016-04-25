=================
availability zone
=================

An **availability zone** is a logical partition of cloud block storage,
compute and network services.

Block Storage v2, Compute v2, Network v2

availability zone list
----------------------

List availability zones and their status

.. program availability zone list
.. code:: bash

    os availability zone list
        [--compute]
        [--network]
        [--volume]
        [--long]

.. option:: --compute

    List compute availability zones

.. option:: --network

    List network availability zones

.. option:: --volume

    List volume availability zones

.. option:: --long

    List additional fields in output
