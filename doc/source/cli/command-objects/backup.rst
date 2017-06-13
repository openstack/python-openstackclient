======
backup
======

Block Storage v1, v2

backup create
-------------

Create new backup
(Deprecated, please use ``volume backup create`` instead)

.. program:: backup create
.. code:: bash

    openstack backup create
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

.. _backup_create-backup:
.. describe:: <volume>

    Volume to backup (name or ID)

backup delete
-------------

Delete backup(s)
(Deprecated, please use ``volume backup delete`` instead)

.. program:: backup delete
.. code:: bash

    openstack backup delete
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
(Deprecated, please use ``volume backup list`` instead)

.. program:: backup list
.. code:: bash

    openstack backup list

.. _backup_list-backup:
.. option:: --long

    List additional fields in output

backup restore
--------------

Restore backup
(Deprecated, please use ``volume backup restore`` instead)

.. program:: backup restore
.. code:: bash

    openstack backup restore
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
(Deprecated, please use ``volume backup show`` instead)

.. program:: backup show
.. code:: bash

    openstack backup show
        <backup>

.. _backup_show-backup:
.. describe:: <backup>

    Backup to display (name or ID)
