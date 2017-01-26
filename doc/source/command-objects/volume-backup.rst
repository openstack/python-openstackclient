=============
volume backup
=============

Block Storage v1, v2

volume backup create
--------------------

Create new volume backup

.. program:: volume backup create
.. code:: bash

    openstack volume backup create
        [--container <container>]
        [--name <name>]
        [--description <description>]
        [--snapshot <snapshot>]
        [--force]
        [--incremental]
        <volume>

.. option:: --container <container>

    Optional backup container name

.. option:: --name <name>

    Name of the backup

.. option:: --description <description>

    Description of the backup

.. option:: --snapshot <snapshot>

    Snapshot to backup (name or ID)

    *Volume version 2 only*

.. option:: --force

    Allow to back up an in-use volume

    *Volume version 2 only*

.. option:: --incremental

    Perform an incremental backup

    *Volume version 2 only*

.. _volume_backup_create-backup:
.. describe:: <volume>

    Volume to backup (name or ID)

volume backup delete
--------------------

Delete volume backup(s)

.. program:: volume backup delete
.. code:: bash

    openstack volume backup delete
        [--force]
        <backup> [<backup> ...]

.. option:: --force

    Allow delete in state other than error or available

    *Volume version 2 only*

.. _volume_backup_delete-backup:
.. describe:: <backup>

    Backup(s) to delete (name or ID)

volume backup list
------------------

List volume backups

.. program:: volume backup list
.. code:: bash

    openstack volume backup list
        [--long]
        [--name <name>]
        [--status <status>]
        [--volume <volume>]
        [--marker <marker>]
        [--limit <limit>]
        [--all-projects]

.. _volume_backup_list-backup:
.. option:: --long

    List additional fields in output

.. option:: --name <name>

    Filters results by the backup name

.. option:: --status <status>

    Filters results by the backup status
    ('creating', 'available', 'deleting', 'error', 'restoring' or 'error_restoring')

.. option:: --volume <volume>

    Filters results by the volume which they backup (name or ID)"

.. option:: --marker <marker>

    The last backup of the previous page (name or ID)

    *Volume version 2 only*

.. option:: --limit <limit>

    Maximum number of backups to display

    *Volume version 2 only*

.. option:: --all-projects

    Include all projects (admin only)

volume backup restore
---------------------

Restore volume backup

.. program:: volume backup restore
.. code:: bash

    openstack volume backup restore
        <backup>
        <volume>

.. _volume_backup_restore-backup:
.. describe:: <backup>

    Backup to restore (name or ID)

.. describe:: <volume>

    Volume to restore to (name or ID)

volume backup set
-----------------

Set volume backup properties

.. program:: volume backup set
.. code:: bash

    openstack volume backup set
        [--name <name>]
        [--description <description>]
        [--state <state>]
        <backup>

.. option:: --name <name>

    New backup name

.. option:: --description <description>

    New backup description

.. option:: --state <state>

    New backup state ("available" or "error") (admin only)
    (This option simply changes the state of the backup in the database with
    no regard to actual status, exercise caution when using)

.. _backup_set-volume-backup:
.. describe:: <backup>

    Backup to modify (name or ID)

volume backup show
------------------

Display volume backup details

.. program:: volume backup show
.. code:: bash

    openstack volume backup show
        <backup>

.. _volume_backup_show-backup:
.. describe:: <backup>

    Backup to display (name or ID)
