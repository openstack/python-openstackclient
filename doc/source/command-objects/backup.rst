======
backup
======

Block Storage v1, v2

backup create
-------------

Create new backup

.. program:: backup create
.. code:: bash

    os backup create
        [--container <container>]
        [--name <name>]
        [--description <description>]
        [--snapshot <snapshot>]
        [--force]
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

.. _backup_create-backup:
.. describe:: <volume>

    Volume to backup (name or ID)

backup delete
-------------

Delete backup(s)

.. program:: backup delete
.. code:: bash

    os backup delete
        [--force]
        <backup> [<backup> ...]

.. option:: --force

    Allow delete in state other than error or available

    *Volume version 2 only*

.. _backup_delete-backup:
.. describe:: <backup>

    Backup(s) to delete (name or ID)

backup list
-----------

List backups

.. program:: backup list
.. code:: bash

    os backup list

.. _backup_list-backup:
.. option:: --long

    List additional fields in output

backup restore
--------------

Restore backup

.. program:: backup restore
.. code:: bash

    os backup restore
        <backup>
        <volume>

.. _backup_restore-backup:
.. describe:: <backup>

    Backup to restore (name or ID)

.. describe:: <volume>

    Volume to restore to (name or ID)

backup show
-----------

Display backup details

.. program:: backup show
.. code:: bash

    os backup show
        <backup>

.. _backup_show-backup:
.. describe:: <backup>

    Backup to display (name or ID)
