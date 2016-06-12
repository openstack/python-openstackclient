==============
security group
==============

A **security group** acts as a virtual firewall for servers and other
resources on a network. It is a container for security group rules
which specify the network access rules.

Compute v2, Network v2

security group create
---------------------

Create a new security group

.. program:: security group create
.. code:: bash

    os security group create
        [--description <description>]
        [--project <project> [--project-domain <project-domain>]]
        <name>

.. option:: --description <description>

    Security group description

.. option:: --project <project>

    Owner's project (name or ID)

    *Network version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    *Network version 2 only*

.. describe:: <name>

    New security group name

security group delete
---------------------

Delete security group(s)

.. program:: security group delete
.. code:: bash

    os security group delete
        <group> [<group> ...]

.. describe:: <group>

    Security group(s) to delete (name or ID)

security group list
-------------------

List security groups

.. program:: security group list
.. code:: bash

    os security group list
        [--all-projects]

.. option:: --all-projects

    Display information from all projects (admin only)

    *Network version 2 ignores this option and will always display information*
    *for all projects (admin only).*

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
