===========
subnet pool
===========

A **subnet pool** contains a collection of prefixes in CIDR notation
that are available for IP address allocation.

Network v2

subnet pool create
------------------

Create subnet pool

.. program:: subnet pool create
.. code:: bash

    os subnet pool create
        [--default-prefix-length <default-prefix-length>]
        [--min-prefix-length <min-prefix-length>]
        [--max-prefix-length <max-prefix-length>]
        [--description <description>]
        [--project <project> [--project-domain <project-domain>]]
        [--address-scope <address-scope>]
        [--default | --no-default]
        [--share | --no-share]
        --pool-prefix <pool-prefix> [...]
        <name>

.. option:: --default-prefix-length <default-prefix-length>

    Set subnet pool default prefix length

.. option:: --min-prefix-length <min-prefix-length>

    Set subnet pool minimum prefix length

.. option:: --max-prefix-length <max-prefix-length>

    Set subnet pool maximum prefix length

.. option:: --description <description>

    Set subnet pool description

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID). This can be used in case
    collisions between project names exist.

.. option:: --address-scope <address-scope>

    Set address scope associated with the subnet pool (name or ID),
    prefixes must be unique across address scopes

.. option:: --default

    Set this as a default subnet pool

.. option:: --no-default

    Set this as a non-default subnet pool

.. option:: --share

    Set this subnet pool as shared

.. option:: --no-share

    Set this subnet pool as not shared

.. describe:: --pool-prefix <pool-prefix>

    Set subnet pool prefixes (in CIDR notation)
    (repeat option to set multiple prefixes)

.. _subnet_pool_create-name:
.. describe:: <name>

    Name of the new subnet pool

subnet pool delete
------------------

Delete subnet pool(s)

.. program:: subnet pool delete
.. code:: bash

    os subnet pool delete
        <subnet-pool> [<subnet-pool> ...]

.. _subnet_pool_delete-subnet-pool:
.. describe:: <subnet-pool>

    Subnet pool(s) to delete (name or ID)

subnet pool list
----------------

List subnet pools

.. program:: subnet pool list
.. code:: bash

    os subnet pool list
        [--long]
        [--share | --no-share]
        [--default | --no-default]
        [--project <project> [--project-domain <project-domain>]]
        [--name <name>]
        [--address-scope <address-scope>]

.. option:: --long

    List additional fields in output

.. option:: --share

    List subnets shared between projects

.. option:: --no-share

    List subnets not shared between projects

.. option:: --default

    List subnets used as the default external subnet pool

.. option:: --no-default

    List subnets not used as the default external subnet pool

.. option:: --project <project>

    List subnets according to their project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --name <name>

    List only subnets of given name in output

.. option:: --address-scope <address-scope>

    List only subnets of given address scope (name or ID) in output

subnet pool set
---------------

Set subnet pool properties

.. program:: subnet pool set
.. code:: bash

    os subnet pool set
        [--name <name>]
        [--pool-prefix <pool-prefix> [...]]
        [--default-prefix-length <default-prefix-length>]
        [--min-prefix-length <min-prefix-length>]
        [--max-prefix-length <max-prefix-length>]
        [--address-scope <address-scope> | --no-address-scope]
        [--default | --no-default]
        [--description <description>]
        <subnet-pool>

.. option:: --name <name>

    Set subnet pool name

.. option:: --pool-prefix <pool-prefix>

    Set subnet pool prefixes (in CIDR notation)
    (repeat option to set multiple prefixes)

.. option:: --default-prefix-length <default-prefix-length>

    Set subnet pool default prefix length

.. option:: --min-prefix-length <min-prefix-length>

    Set subnet pool minimum prefix length

.. option:: --max-prefix-length <max-prefix-length>

    Set subnet pool maximum prefix length

.. option:: --address-scope <address-scope>

    Set address scope associated with the subnet pool (name or ID),
    prefixes must be unique across address scopes

.. option:: --no-address-scope

    Remove address scope associated with the subnet pool

.. option:: --default

    Set this as a default subnet pool

.. option:: --no-default

    Set this as a non-default subnet pool

.. option:: --description <description>

    Set subnet pool description

.. _subnet_pool_set-subnet-pool:
.. describe:: <subnet-pool>

    Subnet pool to modify (name or ID)

subnet pool show
----------------

Display subnet pool details

.. program:: subnet pool show
.. code:: bash

    os subnet pool show
        <subnet-pool>

.. _subnet_pool_show-subnet-pool:
.. describe:: <subnet-pool>

    Subnet pool to display (name or ID)

subnet pool unset
-----------------

Unset subnet pool properties

.. program:: subnet pool unset
.. code:: bash

    os subnet pool unset
        [--pool-prefix <pool-prefix> [...]]
        <subnet-pool>

.. option:: --pool-prefix <pool-prefix>

    Remove subnet pool prefixes (in CIDR notation).
    (repeat option to unset multiple prefixes).

.. _subnet_pool_unset-subnet-pool:
.. describe:: <subnet-pool>

    Subnet pool to modify (name or ID)
