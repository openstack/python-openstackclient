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

    openstack security group create
        [--description <description>]
        [--project <project> [--project-domain <project-domain>]]
        [--tag <tag> | --no-tag]
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

.. option:: --tag <tag>

    Tag to be added to the security group (repeat option to set multiple tags)

    *Network version 2 only*

.. option:: --no-tag

    No tags associated with the security group

    *Network version 2 only*

.. describe:: <name>

    New security group name

security group delete
---------------------

Delete security group(s)

.. program:: security group delete
.. code:: bash

    openstack security group delete
        <group> [<group> ...]

.. describe:: <group>

    Security group(s) to delete (name or ID)

security group list
-------------------

List security groups

.. program:: security group list
.. code:: bash

    openstack security group list
        [--all-projects]
        [--project <project> [--project-domain <project-domain>]]
        [--tags <tag>[,<tag>,...]] [--any-tags <tag>[,<tag>,...]]
        [--not-tags <tag>[,<tag>,...]] [--not-any-tags <tag>[,<tag>,...]]

.. option:: --all-projects

    Display information from all projects (admin only)

    *Network version 2 ignores this option and will always display information*
    *for all projects (admin only).*

.. option:: --project <project>

    List security groups according to the project (name or ID)

    *Network version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    *Network version 2 only*

.. option:: --tags <tag>[,<tag>,...]

    List security groups which have all given tag(s)

    *Network version 2 only*

.. option:: --any-tags <tag>[,<tag>,...]

    List security groups which have any given tag(s)

    *Network version 2 only*

.. option:: --not-tags <tag>[,<tag>,...]

    Exclude security groups which have all given tag(s)

    *Network version 2 only*

.. option:: --not-any-tags <tag>[,<tag>,...]

    Exclude security groups which have any given tag(s)

    *Network version 2 only*

security group set
------------------

Set security group properties

.. program:: security group set
.. code:: bash

    openstack security group set
        [--name <new-name>]
        [--description <description>]
        [--tag <tag>] [--no-tag]
        <group>

.. option:: --name <new-name>

    New security group name

.. option:: --description <description>

    New security group description

.. option:: --tag <tag>

    Tag to be added to the security group (repeat option to set multiple tags)

.. option:: --no-tag

    Clear tags associated with the security group. Specify both --tag
    and --no-tag to overwrite current tags

.. describe:: <group>

    Security group to modify (name or ID)

security group show
-------------------

Display security group details

.. program:: security group show
.. code:: bash

    openstack security group show
        <group>

.. describe:: <group>

    Security group to display (name or ID)

security group unset
--------------------

Unset security group properties

.. program:: security group unset
.. code:: bash

    openstack security group unset
        [--tag <tag> | --all-tag]
        <group>

.. option:: --tag <tag>

    Tag to be removed from the security group
    (repeat option to remove multiple tags)

.. option:: --all-tag

    Clear all tags associated with the security group

.. describe:: <group>

    Security group to modify (name or ID)
