======================
network flavor profile
======================

A **network flavor profile** allows administrators to create, delete, list,
show and update network service profile, which details a framework to enable
operators to configure and users to select from different abstract
representations of a service implementation in the Networking service.
It decouples the logical configuration from its instantiation enabling
operators to create user options according to deployment needs.

Network v2

network flavor profile create
-----------------------------

Create a new network flavor profile

.. program:: network flavor profile create
.. code:: bash

    openstack network flavor profile create
        [--project <project> [--project-domain <project-domain>]]
        [--description <description>]
        [--enable | --disable]
        (--driver <driver> | --metainfo <metainfo> | --driver <driver> --metainfo <metainfo>)

.. option:: --project <project>

    Owner's project (name or ID)

    *Network version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID). This can
    be used in case collisions between project names
    exist

.. option:: --description <description>

    Description for the flavor profile

    *Network version 2 only*

.. option:: --enable

    Enable the flavor profile (default)

.. option:: --disable

    Disable the flavor profile

.. option:: --driver <driver>

    Python module path to driver

    *Network version 2 only*

.. option:: --metainfo <metainfo>

    Metainfo for the flavor profile

    *Network version 2 only*


network flavor profile delete
-----------------------------

Delete network flavor profile

.. program:: network flavor profile delete
.. code:: bash

    openstack network flavor profile delete
        <flavor-profile-id> [<flavor-profile-id> ...]

.. describe:: <flavor-profile-id>

    Flavor profile(s) to delete (ID only)

network flavor profile list
---------------------------

List network flavor profiles

.. program:: network flavor profile list
.. code:: bash

    openstack network flavor profile list

network flavor profile set
--------------------------

Set network flavor profile properties

.. program:: network flavor profile set
.. code:: bash

    openstack network flavor profile set
        [--description <description>]
        [--driver <driver>]
        [--enable | --disable]
        [--metainfo <metainfo>]
        <flavor-profile-id>


.. option:: --description <description>

    Description of the flavor profile

.. option:: --driver <driver>

    Python module path to driver

.. option:: --enable (Default)

    Enable the flavor profile

.. option:: --disable

    Disable the flavor profile

.. option:: --metainfo <metainfo>

    Metainfo for the flavor profile

.. describe:: <flavor-profile-id>

    Flavor profile to update (ID only)

network flavor profile show
---------------------------

Show network flavor profile

.. program:: network flavor profile show
.. code:: bash

    openstack network flavor profile show
        <flavor-profile-id>

.. describe:: <flavor-profile-id>

    Flavor profile to display (ID only)
