======
volume
======

Block Storage v1, v2

volume create
-------------

Create new volume

.. program:: volume create
.. code:: bash

    openstack volume create
        [--size <size>]
        [--type <volume-type>]
        [--image <image> | --snapshot <snapshot> | --source <volume> ]
        [--description <description>]
        [--availability-zone <availability-zone>]
        [--consistency-group <consistency-group>]
        [--property <key=value> [...] ]
        [--hint <key=value> [...] ]
        [--bootable | --non-bootable]
        [--read-only | --read-write]
        <name>

.. option:: --size <size>

    Volume size in GB
    (Required unless --snapshot or --source is specified)

.. option:: --type <volume-type>

    Set the type of volume

    Select ``<volume-type>`` from the available types as shown
    by ``volume type list``.

.. option:: --image <image>

    Use ``<image>`` as source of volume (name or ID)

    This is commonly used to create a boot volume for a server.

.. option:: --snapshot <snapshot>

    Use ``<snapshot>`` as source of volume (name or ID)

.. option:: --source <volume>

    Volume to clone (name or ID)

.. option:: --description <description>

    Volume description

.. option:: --availability-zone <availability-zone>

    Create volume in ``<availability-zone>``

.. option:: --consistency-group <consistency-group>

    Consistency group where the new volume belongs to

.. option:: --property <key=value>

    Set a property on this volume (repeat option to set multiple properties)

.. option:: --hint <key=value>

    Arbitrary scheduler hint key-value pairs to help boot an instance
    (repeat option to set multiple hints)

.. option:: --bootable

    Mark volume as bootable

.. option:: --non-bootable

    Mark volume as non-bootable (default)

.. option:: --read-only

    Set volume to read-only access mode

.. option:: --read-write

    Set volume to read-write access mode (default)

.. _volume_create-name:
.. describe:: <name>

    Volume name

volume delete
-------------

Delete volume(s)

.. program:: volume delete
.. code:: bash

    openstack volume delete
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

    openstack volume list
        [--project <project> [--project-domain <project-domain>]]
        [--user <user> [--user-domain <user-domain>]]
        [--name <name>]
        [--status <status>]
        [--all-projects]
        [--long]
        [--limit <num-volumes>]
        [--marker <volume>]

.. option:: --project <project>

    Filter results by ``<project>`` (name or ID) (admin only)

    *Volume version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).

    This can be used in case collisions between project names exist.

    *Volume version 2 only*

.. option:: --user <user>

    Filter results by ``<user>`` (name or ID) (admin only)

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

.. option:: --limit <num-volumes>

    Maximum number of volumes to display

.. option:: --marker <volume>

    The last volume ID of the previous page

    *Volume version 2 only*

volume migrate
--------------

Migrate volume to a new host

.. program:: volume migrate
.. code:: bash

    openstack volume migrate
        --host <host>
        [--force-host-copy]
        [--lock-volume]
        <volume>

.. option:: --host <host>

    Destination host (takes the form: host@backend-name#pool) (required)

.. option:: --force-host-copy

    Enable generic host-based force-migration,
    which bypasses driver optimizations

.. option:: --lock-volume

    If specified, the volume state will be locked and will not allow
    a migration to be aborted (possibly by another operation)

    *Volume version 2 only*

.. _volume_migrate-volume:
.. describe:: <volume>

    Volume to migrate (name or ID)

volume set
----------

Set volume properties

.. program:: volume set
.. code:: bash

    openstack volume set
        [--name <name>]
        [--size <size>]
        [--description <description>]
        [--no-property]
        [--property <key=value> [...] ]
        [--image-property <key=value> [...] ]
        [--state <state>]
        [--attached | --detached ]
        [--type <volume-type>]
        [--retype-policy <retype-policy>]
        [--bootable | --non-bootable]
        [--read-only | --read-write]
        <volume>

.. option:: --name <name>

    New volume name

.. option:: --size <size>

    Extend volume size in GB

.. option:: --description <description>

    New volume description

.. option:: --no-property

    Remove all properties from :ref:`\<volume\> <volume_set-volume>`
    (specify both :option:`--no-property` and :option:`--property` to
    remove the current properties before setting new properties.)

.. option:: --property <key=value>

    Set a property on this volume (repeat option to set multiple properties)

.. option:: --type <volume-type>

    New volume type (name or ID)

    *Volume version 2 only*

.. option:: --retype-policy <retype-policy>

    Migration policy while re-typing volume
    ("never" or "on-demand", default is "never" )
    (available only when :option:`--type` option is specified)

    *Volume version 2 only*

.. option:: --bootable

    Mark volume as bootable

.. option:: --non-bootable

    Mark volume as non-bootable

.. option:: --read-only

    Set volume to read-only access mode

.. option:: --read-write

    Set volume to read-write access mode

.. option:: --image-property <key=value>

    Set an image property on this volume
    (repeat option to set multiple image properties)

    Image properties are copied along with the image when creating a volume
    using ``--image``.  Note that these properties are immutable on the image
    itself, this option updates the copy attached to this volume.

    *Volume version 2 only*

.. option:: --state <state>

    New volume state
    ("available", "error", "creating", "deleting", "in-use",
    "attaching", "detaching", "error_deleting" or "maintenance") (admin only)
    (This option simply changes the state of the volume in the database with
    no regard to actual status, exercise caution when using)

    *Volume version 2 only*

.. option:: --attached

    Set volume attachment status to "attached" (admin only)
    (This option simply changes the state of the volume in the database with
    no regard to actual status, exercise caution when using)

    *Volume version 2 only*

.. option:: --deattach

    Set volume attachment status to "detached" (admin only)
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

    openstack volume show
        <volume>

.. _volume_show-volume:
.. describe:: <volume>

    Volume to display (name or ID)

volume unset
------------

Unset volume properties

.. program:: volume unset
.. code:: bash

    openstack volume unset
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

Block Storage v3

 .. autoprogram-cliff:: openstack.volume.v3
     :command: volume summary

 .. autoprogram-cliff:: openstack.volume.v3
     :command: volume revert
