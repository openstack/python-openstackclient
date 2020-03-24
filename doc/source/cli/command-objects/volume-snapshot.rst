===============
volume snapshot
===============

Block Storage v1, v2

volume snapshot create
----------------------

Create new volume snapshot

.. program:: volume snapshot create
.. code:: bash

    openstack volume snapshot create
        [--volume <volume>]
        [--description <description>]
        [--force]
        [--property <key=value> [...] ]
        [--remote-source <key=value> [...]]
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

.. option:: --remote-source <key=value>

    The attribute(s) of the exsiting remote volume snapshot
    (admin required) (repeat option to specify multiple attributes)
    e.g.: '--remote-source source-name=test_name --remote-source source-id=test_id'

    *Volume version 2 only*

.. _volume_snapshot_create-snapshot-name:
.. describe:: <snapshot-name>

    Name of the new snapshot

volume snapshot delete
----------------------

Delete volume snapshot(s)

.. program:: volume snapshot delete
.. code:: bash

    openstack volume snapshot delete
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

    openstack volume snapshot list
        [--all-projects]
        [--project <project> [--project-domain <project-domain>]]
        [--long]
        [--limit <num-snapshots>]
        [--marker <snapshot>]
        [--name <name>]
        [--status <status>]
        [--volume <volume>]

.. option:: --all-projects

    Include all projects (admin only)

.. option:: --project <project>

    Filter results by project (name or ID) (admin only)

    *Volume version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).

    This can be used in case collisions between project names exist.

    *Volume version 2 only*

.. option:: --long

    List additional fields in output

.. option:: --status <status>

    Filters results by a status.
    ('available', 'error', 'creating', 'deleting' or 'error_deleting')

.. option:: --name <name>

    Filters results by a name.

.. option:: --volume <volume>

    Filters results by a volume (name or ID).

.. option:: --limit <num-snapshots>

    Maximum number of snapshots to display

    *Volume version 2 only*

.. option:: --marker <snapshot>

    The last snapshot ID of the previous page

    *Volume version 2 only*

volume snapshot set
-------------------

Set volume snapshot properties

.. program:: volume snapshot set
.. code:: bash

    openstack volume snapshot set
        [--name <name>]
        [--description <description>]
        [--no-property]
        [--property <key=value> [...] ]
        [--state <state>]
        <snapshot>

.. option:: --name <name>

    New snapshot name

.. option:: --description <description>

    New snapshot description

.. option:: --no-property

    Remove all properties from :ref:`\<snapshot\> <volume_snapshot_set-snapshot>`
    (specify both :option:`--no-property` and :option:`--property` to
    remove the current properties before setting new properties.)

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

    openstack volume snapshot show
        <snapshot>

.. _volume_snapshot_show-snapshot:
.. describe:: <snapshot>

    Snapshot to display (name or ID)

volume snapshot unset
---------------------

Unset volume snapshot properties

.. program:: volume snapshot unset
.. code:: bash

    openstack volume snapshot unset
        [--property <key>]
        <snapshot>

.. option:: --property <key>

    Property to remove from snapshot (repeat option to remove multiple properties)

.. _volume_snapshot_unset-snapshot:
.. describe:: <snapshot>

    Snapshot to modify (name or ID)
