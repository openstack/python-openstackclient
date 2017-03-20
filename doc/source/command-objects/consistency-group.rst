=================
consistency group
=================

Block Storage v2

consistency group add volume
----------------------------

Add volume(s) to consistency group.

.. program:: consistency group add volume
.. code:: bash

    openstack consistency group add volume
        <consistency-group>
        <volume> [<volume> ...]

.. _consistency_group_add_volume:
.. describe:: <consistency-group>

    Consistency group to contain <volume> (name or ID)

.. describe:: <volume>

    Volume(s) to add to <consistency-group> (name or ID)
    (repeat option to add multiple volumes)

consistency group create
------------------------

Create new consistency group.

.. program:: consistency group create
.. code:: bash

    openstack consistency group create
        --volume-type <volume-type> | --consistency-group-source <consistency-group> | --consistency-group-snapshot <consistency-group-snapshot>
        [--description <description>]
        [--availability-zone <availability-zone>]
        [<name>]

.. option:: --volume-type <volume-type>

    Volume type of this consistency group (name or ID)

.. option:: --consistency-group-source <consistency-group>

    Existing consistency group (name or ID)

.. option:: --consistency-group-snapshot <consistency-group-snapshot>

    Existing consistency group snapshot (name or ID)

.. option:: --description <description>

    Description of this consistency group

.. option:: --availability-zone <availability-zone>

    Availability zone for this consistency group
    (not available if creating consistency group from source)

.. _consistency_group_create-name:
.. describe:: <name>

    Name of new consistency group (default to None)

consistency group delete
------------------------

Delete consistency group(s).

.. program:: consistency group delete
.. code:: bash

    openstack consistency group delete
        [--force]
        <consistency-group> [<consistency-group> ...]

.. option:: --force

    Allow delete in state other than error or available

.. _consistency_group_delete-consistency-group:
.. describe:: <consistency-group>

    Consistency group(s) to delete (name or ID)

consistency group list
----------------------

List consistency groups.

.. program:: consistency group list
.. code:: bash

    openstack consistency group list
        [--all-projects]
        [--long]

.. option:: --all-projects

    Show detail for all projects. Admin only.
    (defaults to False)

.. option:: --long

    List additional fields in output

consistency group remove volume
-------------------------------

Remove volume(s) from consistency group.

.. program:: consistency group remove volume
.. code:: bash

    openstack consistency group remove volume
        <consistency-group>
        <volume> [<volume> ...]

.. _consistency_group_remove_volume:
.. describe:: <consistency-group>

    Consistency group containing <volume> (name or ID)

.. describe:: <volume>

    Volume(s) to remove from <consistency-group> (name or ID)
    (repeat option to remove multiple volumes)

consistency group set
---------------------

Set consistency group properties.

.. program:: consistency group set
.. code:: bash

    openstack consistency group set
        [--name <name>]
        [--description <description>]
        <consistency-group>

.. option:: --name <name>

    New consistency group name

.. option:: --description <description>

    New consistency group description

.. _consistency_group_set-consistency-group:
.. describe:: <consistency-group>

    Consistency group to modify (name or ID)

consistency group show
----------------------

Display consistency group details.

.. program:: consistency group show
.. code:: bash

    openstack consistency group show
        <consistency-group>

.. _consistency_group_show-consistency-group:
.. describe:: <consistency-group>

    Consistency group to display (name or ID)
