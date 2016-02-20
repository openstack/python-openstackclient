=============
server backup
=============

A server backup is a disk image created in the Image store from a running server
instance.  The backup command manages the number of archival copies to retain.

Compute v2

server backup create
--------------------

Create a server backup image

.. program:: server create
.. code:: bash

    os server backup create
        [--name <image-name>]
        [--type <backup-type>]
        [--rotate <count>]
        [--wait]
        <server>

.. option:: --name <image-name>

    Name of the backup image (default: server name)

.. option:: --type <backup-type>

    Used to populate the ``backup_type`` property of the backup
    image (default: empty)

.. option:: --rotate <count>

    Number of backup images to keep (default: 1)

.. option:: --wait

    Wait for operation to complete

.. describe:: <server>

    Server to back up (name or ID)
