========
snapshot
========

Block Storage v1, v2

snapshot create
---------------

Create new snapshot
(Deprecated, please use ``volume snapshot create`` instead)

.. program:: snapshot create
.. code:: bash

    openstack snapshot create
        [--name <name>]
        [--description <description>]
        [--force]
        [--property <key=value> [...] ]
        <volume>

.. option:: --name <name>

    Name of the snapshot

.. option:: --description <description>

    Description of the snapshot

.. option:: --force

    Create a snapshot attached to an instance. Default is False

.. option:: --property <key=value>

    Set a property to this snapshot (repeat option to set multiple properties)

    *Volume version 2 only*

.. _snapshot_create-snapshot:
.. describe:: <volume>

    Volume to snapshot (name or ID)

snapshot delete
---------------

Delete snapshot(s)
(Deprecated, please use ``volume snapshot delete`` instead)

.. program:: snapshot delete
.. code:: bash

    openstack snapshot delete
        <snapshot> [<snapshot> ...]

.. _snapshot_delete-snapshot:
.. describe:: <snapshot>

    Snapshot(s) to delete (name or ID)

snapshot list
-------------

List snapshots
(Deprecated, please use ``volume snapshot list`` instead)

.. program:: snapshot list
.. code:: bash

    openstack snapshot list
        [--all-projects]
        [--long]
        [--limit <limit>]
        [--marker <marker>]

.. option:: --all-projects

    Include all projects (admin only)

.. option:: --long

    List additional fields in output

.. option:: --limit <limit>

    Maximum number of snapshots to display

    *Volume version 2 only*

.. option:: --marker <marker>

    The last snapshot ID of the previous page

    *Volume version 2 only*

snapshot set
------------

Set snapshot properties
(Deprecated, please use ``volume snapshot set`` instead)

.. program:: snapshot set
.. code:: bash

    openstack snapshot set
        [--name <name>]
        [--description <description>]
        [--property <key=value> [...] ]
        [--state <state>]
        <snapshot>

.. _snapshot_restore-snapshot:
.. option:: --name <name>

    New snapshot name

.. option:: --description <description>

    New snapshot description

.. option:: --property <key=value>

    Property to add or modify for this snapshot (repeat option to set multiple properties)

.. option:: --state <state>

    New snapshot state.
    ("available", "error", "creating", "deleting", or "error_deleting") (admin only)
    (This option simply changes the state of the snapshot in the database with
    no regard to actual status, exercise caution when using)

    *Volume version 2 only*

.. describe:: <snapshot>

    Snapshot to modify (name or ID)

snapshot show
-------------

Display snapshot details
(Deprecated, please use ``volume snapshot show`` instead)

.. program:: snapshot show
.. code:: bash

    openstack snapshot show
        <snapshot>

.. _snapshot_show-snapshot:
.. describe:: <snapshot>

    Snapshot to display (name or ID)

snapshot unset
--------------

Unset snapshot properties
(Deprecated, please use ``volume snapshot unset`` instead)

.. program:: snapshot unset
.. code:: bash

    openstack snapshot unset
        [--property <key>]
        <snapshot>

.. option:: --property <key>

    Property to remove from snapshot (repeat option to remove multiple properties)

.. describe:: <snapshot>

    Snapshot to modify (name or ID)
