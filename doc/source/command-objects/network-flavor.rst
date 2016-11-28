==============
network flavor
==============

A **network flavor** extension allows the user selection of operator-curated
flavors during resource creations. It allows administrators to create network
service flavors.

Network v2

network flavor add profile
--------------------------

Add network flavor to service profile

.. program:: network flavor add profile
.. code:: bash

    openstack network flavor add profile
        <flavor>
        <service-profile-id>

.. describe:: <flavor>

    Flavor to which service profile is added. (Name or ID)

.. describe:: <service-profile-id>

    Service profile to be added to flavor. (ID only)

.. _network_flavor_add_profile:

network flavor create
---------------------

Create network flavor

.. program:: network flavor create
.. code:: bash

    openstack network flavor create
        --service-type <service-type>
        [--description <description>]
        [--enable | --disable]
        [--project <project> [--project-domain <project-domain>]]
        <name>

.. option:: --service-type <service-type>

    Service type to which the flavor applies to: e.g. VPN.
    (See openstack :ref:`\<service providers\> <network_service_provider_list>`) (required)

.. option:: --description <description>

    Description for the flavor

.. option:: --enable

    Enable the flavor (default)

.. option:: --disable

    Disable the flavor

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID). This can
    be used in case collisions between project names
    exist.

.. describe:: <name>

    Name for the flavor

.. _network_flavor_create:

network flavor delete
---------------------

Delete network flavor(s)

.. program:: network flavor delete
.. code:: bash

    openstack network flavor delete
        <flavor> [<flavor> ...]

.. describe:: <flavor>

    Flavor(s) to delete (name or ID)

.. _network_flavor_delete:

network flavor list
-------------------

List network flavors

.. program:: network flavor list
.. code:: bash

    openstack network flavor list

.. _network_flavor_list:

network flavor remove profile
-----------------------------

Remove network flavor from service profile

.. program:: network flavor remove profile
.. code:: bash

    openstack network flavor remove profile
        <flavor>
        <service-profile-id>

.. describe:: <flavor>

    Flavor from which service profile is removed. (Name or ID)

.. describe:: <service-profile-id>

    Service profile to be removed from flavor. (ID only)

.. _network_flavor_remove_profile:

network flavor set
------------------

Set network flavor properties

.. program:: network flavor set
.. code:: bash

    openstack network flavor set
        [--name <name>]
        [--description <description>]
        [--enable | --disable]
        <flavor>

.. option:: --name <name>

    Set flavor name

.. option:: --description <description>

    Set network flavor description

.. option:: --enable

    Enable network flavor

.. option:: --disable

    Disable network flavor

.. describe:: <flavor>

    Flavor to update (name or ID)

.. _network_flavor_set:

network flavor show
-------------------

Show network flavor

.. program:: network flavor show
.. code:: bash

    openstack network flavor show
        <flavor>

.. describe:: <flavor>

    Flavor to display (name or ID)

.. _network_flavor_show:
