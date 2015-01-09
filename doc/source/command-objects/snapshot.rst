========
snapshot
========

Volume v1

snapshot create
---------------

Create new snapshot

.. program:: snapshot create
.. code:: bash

    os snapshot create
        [--name <name>]
        [--description <description>]
        [--force]
        <volume>

.. option:: --name <name>

    Name of the snapshot

.. option:: --description <description>

    Description of the snapshot

.. option:: --force

    Create a snapshot attached to an instance. Default is False

.. _snapshot_create-snapshot:
.. describe:: <volume>

    Volume to snapshot (name or ID)

snapshot delete
---------------

Delete snapshot(s)

.. program:: snapshot delete
.. code:: bash

    os snapshot delete
        <snapshot> [<snapshot> ...]

.. _snapshot_delete-snapshot:
.. describe:: <snapshot>

    Snapshot(s) to delete (name or ID)

snapshot list
-------------

List snapshots

.. program:: snapshot list
.. code:: bash

    os snapshot list

.. option:: --long

    List additional fields in output

snapshot set
------------

Set snapshot properties

.. program:: snapshot set
.. code:: bash

    os snapshot set
        [--name <name>]
        [--description <description>]
        [--property <key=value> [...] ]
        <snapshot>

.. _snapshot_restore-snapshot:
.. option:: --name <name>

    New snapshot name

.. option:: --description <description>

    New snapshot description

.. option:: --property <key=value>

    Property to add or modify for this snapshot (repeat option to set multiple properties)

.. describe:: <snapshot>

    Snapshot to modify (name or ID)

snapshot show
-------------

Display snapshot details

.. program:: snapshot show
.. code:: bash

    os snapshot show
        <snapshot>

.. _snapshot_show-snapshot:
.. describe:: <snapshot>

    Snapshot to display (name or ID)

snapshot unset
--------------

Unset snapshot properties

.. program:: snapshot unset
.. code:: bash

    os snapshot unset
        [--property <key>]
        <snapshot>

.. option:: --property <key>

    Property to remove from snapshot (repeat option to remove multiple properties)

.. describe:: <snapshot>

    Snapshot to modify (name or ID)
