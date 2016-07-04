===============
volume snapshot
===============

Block Storage v1, v2

volume snapshot create
----------------------

Create new volume snapshot

.. program:: volume snapshot create
.. code:: bash

    os volume snapshot create
        [--volume <volume>]
        [--description <description>]
        [--force]
        [--property <key=value> [...] ]
        <snapshot-name>

.. option:: --volume <volume>

    Volume to snapshot (name or ID) (default is <snapshot-name>)

.. option:: --description <description>

    Description of the snapshot

.. option:: --force

    Create a snapshot attached to an instance. Default is False

.. option:: --property <key=value>

    Set a property to this snapshot (repeat option to set multiple properties)

    *Volume version 2 only*

.. _volume_snapshot_create-snapshot-name:
.. describe:: <snapshot-name>

    Name of the new snapshot (default to None)

volume snapshot delete
----------------------

Delete volume snapshot(s)

.. program:: volume snapshot delete
.. code:: bash

    os volume snapshot delete
        [--force]
        <snapshot> [<snapshot> ...]

.. option:: --force

    Attempt forced removal of snapshot(s), regardless of state (defaults to False)

.. _volume_snapshot_delete-snapshot:
.. describe:: <snapshot>

    Snapshot(s) to delete (name or ID)

volume snapshot list
--------------------

List volume snapshots

.. program:: volume snapshot list
.. code:: bash

    os volume snapshot list
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

volume snapshot set
-------------------

Set volume snapshot properties

.. program:: volume snapshot set
.. code:: bash

    os volume snapshot set
        [--name <name>]
        [--description <description>]
        [--property <key=value> [...] ]
        [--state <state>]
        <snapshot>

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

.. _volume_snapshot_set-snapshot:
.. describe:: <snapshot>

    Snapshot to modify (name or ID)

volume snapshot show
--------------------

Display volume snapshot details

.. program:: volume snapshot show
.. code:: bash

    os volume snapshot show
        <snapshot>

.. _volume_snapshot_show-snapshot:
.. describe:: <snapshot>

    Snapshot to display (name or ID)

volume snapshot unset
---------------------

Unset volume snapshot properties

.. program:: volume snapshot unset
.. code:: bash

    os volume snapshot unset
        [--property <key>]
        <snapshot>

.. option:: --property <key>

    Property to remove from snapshot (repeat option to remove multiple properties)

.. _volume_snapshot_unset-snapshot:
.. describe:: <snapshot>

    Snapshot to modify (name or ID)
