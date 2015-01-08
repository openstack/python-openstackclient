======
backup
======

Volume v1

backup create
-------------

Create new backup

.. program:: backup create
.. code:: bash

    os backup create
        [--container <container>]
        [--name <name>]
        [--description <description>]
        <volume>

.. option:: --container <container>

    Optional backup container name

.. option:: --name <name>

    Name of the backup

.. option:: --description <description>

    Description of the backup

.. _backup_create-backup:
.. describe:: <volume>

    Volume to backup (name or ID)

backup delete
-------------

Delete backup(s)

.. program:: backup delete
.. code:: bash

    os backup delete
        <backup> [<backup> ...]

.. _backup_delete-backup:
.. describe:: <backup>

    Backup(s) to delete (ID only)

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

    Backup to restore (ID only)

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

    Backup to display (ID only)
