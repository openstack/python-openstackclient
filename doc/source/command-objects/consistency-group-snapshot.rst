==========================
consistency group snapshot
==========================

Block Storage v2

consistency group snapshot create
---------------------------------

Create new consistency group snapshot.

.. program:: consistency group snapshot create
.. code:: bash

    openstack consistency group snapshot create
        [--consistency-group <consistency-group>]
        [--description <description>]
        [<snapshot-name>]

.. option:: --consistency-group <consistency-group>

    Consistency group to snapshot (name or ID)
    (default to be the same as <snapshot-name>)

.. option:: --description <description>

    Description of this consistency group snapshot

.. _consistency_group_snapshot_create-snapshot-name:
.. describe:: <snapshot-name>

    Name of new consistency group snapshot (default to None)

consistency group snapshot delete
---------------------------------

Delete consistency group snapshot(s)

.. program:: consistency group snapshot delete
.. code:: bash

    openstack consistency group snapshot delete
        <consistency-group-snapshot> [<consistency-group-snapshot> ...]

.. _consistency_group_snapshot_delete-consistency-group-snapshot:
.. describe:: <consistency-group-snapshot>

    Consistency group snapshot(s) to delete (name or ID)

consistency group snapshot list
-------------------------------

List consistency group snapshots.

.. program:: consistency group snapshot list
.. code:: bash

    openstack consistency group snapshot list
        [--all-projects]
        [--long]
        [--status <status>]
        [--consistency-group <consistency-group>]

.. option:: --all-projects

    Show detail for all projects. Admin only.
    (defaults to False)

.. option:: --long

    List additional fields in output

.. option:: --status <status>

    Filters results by a status
    ("available", "error", "creating", "deleting" or "error_deleting")

.. option:: --consistency-group <consistency-group>

    Filters results by a consistency group (name or ID)

consistency group snapshot show
-------------------------------

Display consistency group snapshot details.

.. program:: consistency group snapshot show
.. code:: bash

    openstack consistency group snapshot show
        <consistency-group-snapshot>

.. _consistency_group_snapshot_show-consistency-group-snapshot:
.. describe:: <consistency-group-snapshot>

    Consistency group snapshot to display (name or ID)
