======
volume
======

Block Storage v1, v2

volume create
-------------

Create new volume

.. program:: volume create
.. code:: bash

    os volume create
        [--size <size>]
        [--type <volume-type>]
        [--image <image> | --snapshot <snapshot> | --source <volume> | --source-replicated <replicated-volume>]
        [--description <description>]
        [--user <user>]
        [--project <project>]
        [--availability-zone <availability-zone>]
        [--consistency-group <consistency-group>]
        [--property <key=value> [...] ]
        [--hint <key=value> [...] ]
        [--multi-attach]
        <name>

.. option:: --size <size>

    Volume size in GB
    (Required unless --snapshot or --source or --source-replicated is specified)

.. option:: --type <volume-type>

    Set the type of volume

    Select :option:`\<volume-type\>` from the available types as shown
    by ``volume type list``.

.. option:: --image <image>

    Use :option:`\<image\>` as source of volume (name or ID)

    This is commonly used to create a boot volume for a server.

.. option:: --snapshot <snapshot>

    Use :option:`\<snapshot\>` as source of volume (name or ID)

.. option:: --source <volume>

    Volume to clone (name or ID)

.. option:: --source-replicated <replicated-volume>

    Replicated volume to clone (name or ID)

.. option:: --description <description>

    Volume description

.. option:: --user <user>

    Specify an alternate user (name or ID)

.. option:: --project <project>

    Specify an alternate project (name or ID)

.. option:: --availability-zone <availability-zone>

    Create volume in :option:`\<availability-zone\>`

.. option:: --consistency-group <consistency-group>

    Consistency group where the new volume belongs to

.. option:: --property <key=value>

    Set a property on this volume (repeat option to set multiple properties)

.. option:: --hint <key=value>

    Arbitrary scheduler hint key-value pairs to help boot an instance
    (repeat option to set multiple hints)

.. option:: --multi-attach

    Allow volume to be attached more than once (default to False)

.. _volume_create-name:
.. describe:: <name>

    Volume name

The :option:`--project` and :option:`--user`  options are typically only
useful for admin users, but may be allowed for other users depending on
the policy of the cloud and the roles granted to the user.

volume delete
-------------

Delete volume(s)

.. program:: volume delete
.. code:: bash

    os volume delete
        [--force | --purge]
        <volume> [<volume> ...]

.. option:: --force

    Attempt forced removal of volume(s), regardless of state (defaults to False)

.. option:: --purge

    Remove any snapshots along with volume(s) (defaults to False)

    *Volume version 2 only*

.. _volume_delete-volume:
.. describe:: <volume>

    Volume(s) to delete (name or ID)

volume list
-----------

List volumes

.. program:: volume list
.. code:: bash

    os volume list
        [--project <project> [--project-domain <project-domain>]]
        [--user <user> [--user-domain <user-domain>]]
        [--name <name>]
        [--status <status>]
        [--all-projects]
        [--long]
        [--limit <limit>]
        [--marker <marker>]

.. option:: --project <project>

    Filter results by :option:`\<project\>` (name or ID) (admin only)

    *Volume version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).

    This can be used in case collisions between project names exist.

    *Volume version 2 only*

.. option:: --user <user>

    Filter results by :option:`\<user\>` (name or ID) (admin only)

    *Volume version 2 only*

.. option:: --user-domain <user-domain>

    Domain the user belongs to (name or ID).

    This can be used in case collisions between user names exist.

    *Volume version 2 only*

.. option:: --name <name>

    Filter results by volume name

.. option:: --status <status>

    Filter results by status

.. option:: --all-projects

    Include all projects (admin only)

.. option:: --long

    List additional fields in output

.. option:: --limit <limit>

    Maximum number of volumes to display

.. option:: --marker <marker>

    The last volume ID of the previous page

    *Volume version 2 only*

volume set
----------

Set volume properties

.. program:: volume set
.. code:: bash

    os volume set
        [--name <name>]
        [--size <size>]
        [--description <description>]
        [--property <key=value> [...] ]
        [--image-property <key=value> [...] ]
        [--state <state>]
        [--bootable | --non-bootable]
        <volume>

.. option:: --name <name>

    New volume name

.. option:: --size <size>

    Extend volume size in GB

.. option:: --description <description>

    New volume description

.. option:: --property <key=value>

    Set a property on this volume (repeat option to set multiple properties)

.. option:: --bootable

    Mark volume as bootable

.. option:: --non-bootable

    Mark volume as non-bootable

.. option:: --image-property <key=value>

    Set an image property on this volume
    (repeat option to set multiple image properties)

    Image properties are copied along with the image when creating a volume
    using :option:`--image`.  Note that these properties are immutable on the
    image itself, this option updates the copy attached to this volume.

    *Volume version 2 only*

.. option:: --state <state>

    New volume state
    ("available", "error", "creating", "deleting", "in-use",
    "attaching", "detaching", "error_deleting" or "maintenance") (admin only)
    (This option simply changes the state of the volume in the database with
    no regard to actual status, exercise caution when using)

    *Volume version 2 only*

.. _volume_set-volume:
.. describe:: <volume>

    Volume to modify (name or ID)

volume show
-----------

Show volume details

.. program:: volume show
.. code:: bash

    os volume show
        <volume>

.. _volume_show-volume:
.. describe:: <volume>

    Volume to display (name or ID)

volume unset
------------

Unset volume properties

.. program:: volume unset
.. code:: bash

    os volume unset
        [--property <key>]
        [--image-property <key>]
        <volume>

.. option:: --property <key>

    Remove a property from volume (repeat option to remove multiple properties)

.. option:: --image-property <key>

    Remove an image property from volume
    (repeat option to remove multiple image properties)

    *Volume version 2 only*

.. _volume_unset-volume:
.. describe:: <volume>

    Volume to modify (name or ID)
