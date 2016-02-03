==============
security group
==============

Compute v2, Network v2

security group create
---------------------

Create a new security group

.. program:: security group create
.. code:: bash

    os security group create
        [--description <description>]
        <name>

.. option:: --description <description>

    Security group description

.. describe:: <name>

    New security group name

security group delete
---------------------

Delete a security group

.. program:: security group delete
.. code:: bash

    os security group delete
        <group>

.. describe:: <group>

    Security group to delete (name or ID)

security group list
-------------------

List security groups

.. program:: security group list
.. code:: bash

    os security group list
        [--all-projects]

.. option:: --all-projects

    Display information from all projects (admin only)

security group set
------------------

Set security group properties

.. program:: security group set
.. code:: bash

    os security group set
        [--name <new-name>]
        [--description <description>]
        <group>

.. option:: --name <new-name>

    New security group name

.. option:: --description <description>

    New security group description

.. describe:: <group>

    Security group to modify (name or ID)

security group show
-------------------

Display security group details

.. program:: security group show
.. code:: bash

    os security group show
        <group>

.. describe:: <group>

    Security group to display (name or ID)
