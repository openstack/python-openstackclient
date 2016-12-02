=================
consistency group
=================

Block Storage v2

consistency group create
------------------------

Create new consistency group.

.. program:: consistency group create
.. code:: bash

    os consistency group create
        --volume-type <volume-type> | --consistency-group-source <consistency-group>
        [--description <description>]
        [--availability-zone <availability-zone>]
        [<name>]

.. option:: --volume-type <volume-type>

    Volume type of this consistency group (name or ID)

.. option:: --consistency-group-source <consistency-group>

    Existing consistency group (name or ID)

.. option:: --description <description>

    Description of this consistency group

.. option:: --availability-zone <availability-zone>

    Availability zone for this consistency group
    (not available if creating consistency group from source)

.. _consistency_group_create-name:
.. option:: <name>

    Name of new consistency group (default to None)

consistency group list
----------------------

List consistency groups.

.. program:: consistency group list
.. code:: bash

    os consistency group list
        [--all-projects]
        [--long]

.. option:: --all-projects

    Show detail for all projects. Admin only.
    (defaults to False)

.. option:: --long

    List additional fields in output
