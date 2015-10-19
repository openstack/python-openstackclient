======
volume
======

Volume v1, v2

volume create
-------------

Create new volume

.. program:: volume create
.. code:: bash

    os volume create
        --size <size>
        [--snapshot <snapshot>]
        [--description <description>]
        [--type <volume-type>]
        [--user <user>]
        [--project <project>]
        [--availability-zone <availability-zone>]
        [--image <image>]
        [--source <volume>]
        [--property <key=value> [...] ]
        <name>

.. option:: --size <size> (required)

    New volume size in GB

.. option:: --snapshot <snapshot>

    Use <snapshot> as source of new volume

.. option:: --description <description>

    New volume description

.. option:: --type <volume-type>

    Use <volume-type> as the new volume type

.. option:: --user <user>

    Specify an alternate user (name or ID)

.. option:: --project <project>

    Specify an alternate project (name or ID)

.. option:: --availability-zone <availability-zone>

    Create new volume in <availability-zone>

.. option:: --image <image>

    Use <image> as source of new volume (name or ID)

.. option:: --source <source>

    Volume to clone (name or ID)

.. option:: --property <key=value>

    Set a property on this volume (repeat option to set multiple properties)

.. describe:: <name>

    New volume name

The :option:`--project` and :option:`--user`  options are typically only
useful for admin users, but may be allowed for other users depending on
the policy of the cloud and the roles granted to the user.

volume delete
-------------

Delete volume(s)

.. program:: volume delete
.. code:: bash

    os volume delete
        [--force]
         <volume> [<volume> ...]

.. option:: --force

    Attempt forced removal of volume(s), regardless of state (defaults to False)

.. describe:: <volume>

    Volume(s) to delete (name or ID)

volume list
-----------

List volumes

.. program:: volume list
.. code:: bash

    os volume list
        [--all-projects]
        [--project <project> [--project-domain <project-domain>]]
        [--user <user> [--user-domain <user-domain>]]
        [--name <name>]
        [--status <status>]
        [--long]

.. option:: --project <project>

    Filter results by project (name or ID) (admin only)

    *Volume version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    *Volume version 2 only*

.. option:: --user <user>

    Filter results by user (name or ID) (admin only)

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

volume set
----------

Set volume properties

.. program:: volume set
.. code:: bash

    os volume set
        [--name <name>]
        [--description <description>]
        [--size <size>]
        [--property <key=value> [...] ]
        <volume>

.. option:: --name <name>

    New volume name

.. option:: --description <description>

    New volume description

.. option:: --size <size>

    Extend volume size in GB

.. option:: --property <key=value>

    Property to add or modify for this volume (repeat option to set multiple properties)

.. describe:: <volume>

    Volume to modify (name or ID)

volume show
-----------

Show volume details

.. program:: volume show
.. code:: bash

    os volume show
        <volume>

.. describe:: <volume>

    Volume to display (name or ID)

volume unset
------------

Unset volume properties

.. program:: volume unset
.. code:: bash

    os volume unset
        [--property <key>]
        <volume>

.. option:: --property <key>

    Property to remove from volume (repeat option to remove multiple properties)

.. describe:: <volume>

    Volume to modify (name or ID)
