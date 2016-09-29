=========
aggregate
=========

Host aggregates provide a mechanism to group hosts according to certain
criteria.

Compute v2

aggregate add host
------------------

Add host to aggregate

.. program:: aggregate add host
.. code:: bash

    os aggregate add host
        <aggregate>
        <host>

.. _aggregate_add_host-aggregate:
.. describe:: <aggregate>

    Aggregate (name or ID)

.. describe:: <host>

    Host to add to :ref:`\<aggregate\> <aggregate_add_host-aggregate>`

aggregate create
----------------

Create a new aggregate

.. program:: aggregate create
.. code:: bash

    os aggregate create
        [--zone <availability-zone>]
        [--property <key=value> [...] ]
        <name>

.. option:: --zone <availability-zone>

    Availability zone name

.. option:: --property <key=value>

    Property to add to this aggregate (repeat option to set multiple properties)

.. describe:: <name>

    New aggregate name

aggregate delete
----------------

Delete existing aggregate(s)

.. program:: aggregate delete
.. code:: bash

    os aggregate delete
        <aggregate> [<aggregate> ...]

.. describe:: <aggregate>

    Aggregate(s) to delete (name or ID)

aggregate list
--------------

List all aggregates

.. program:: aggregate list
.. code:: bash

    os aggregate list
        [--long]

.. option:: --long

    List additional fields in output

aggregate remove host
---------------------

Remove host from aggregate

.. program:: aggregate remove host
.. code:: bash

    os aggregate remove host
        <aggregate>
        <host>

.. _aggregate_remove_host-aggregate:
.. describe:: <aggregate>

    Aggregate (name or ID)

.. describe:: <host>

    Host to remove from :ref:`\<aggregate\> <aggregate_remove_host-aggregate>`

aggregate set
-------------

Set aggregate properties

.. program:: aggregate set
.. code:: bash

    os aggregate set
        [--name <new-name>]
        [--zone <availability-zone>]
        [--property <key=value> [...] ]
        [--no-property]
        <aggregate>

.. option:: --name <name>

    Set aggregate name

.. option:: --zone <availability-zone>

    Set availability zone name

.. option:: --property <key=value>

    Property to set on :ref:`\<aggregate\> <aggregate_set-aggregate>`
    (repeat option to set multiple properties)

.. option:: --no-property

    Remove all properties from :ref:`\<aggregate\> <aggregate_set-aggregate>`
    (specify both --property and --no-property to
    overwrite the current properties)

.. _aggregate_set-aggregate:
.. describe:: <aggregate>

    Aggregate to modify (name or ID)

aggregate show
--------------

Display aggregate details

.. program:: aggregate show
.. code:: bash

    os aggregate show
        <aggregate>

.. describe:: <aggregate>

    Aggregate to display (name or ID)

aggregate unset
---------------

Unset aggregate properties

.. program:: aggregate unset
.. code-block:: bash

    os aggregate unset
        [--property <key> [...] ]
        <aggregate>

.. option:: --property <key>

    Property to remove from :ref:`\<aggregate\> <aggregate_unset-aggregate>`
    (repeat option to remove multiple properties)

.. _aggregate_unset-aggregate:
.. describe:: <aggregate>

    Aggregate to modify (name or ID)
