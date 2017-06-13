======
region
======

Identity v3

region create
-------------

Create new region

.. program:: region create
.. code:: bash

    openstack region create
        [--parent-region <region-id>]
        [--description <description>]
        <region-id>

.. option:: --parent-region <region-id>

    Parent region ID

.. option:: --description <description>

    New region description

.. _region_create-region-id:
.. describe:: <region-id>

    New region ID

region delete
-------------

Delete region(s)

.. program:: region delete
.. code:: bash

    openstack region delete
        <region-id> [<region-id> ...]

.. _region_delete-region-id:
.. describe:: <region-id>

    Region ID(s) to delete

region list
-----------

List regions

.. program:: region list
.. code:: bash

    openstack region list
        [--parent-region <region-id>]

.. option:: --parent-region <region-id>

    Filter by parent region ID

region set
----------

Set region properties

.. program:: region set
.. code:: bash

    openstack region set
        [--parent-region <region-id>]
        [--description <description>]
        <region-id>

.. option:: --parent-region <region-id>

    New parent region ID

.. option:: --description <description>

    New region description

.. _region_set-region-id:
.. describe:: <region-id>

    Region to modify

region show
-----------

Display region details

.. program:: region show
.. code:: bash

    openstack region show
        <region-id>

.. _region_show-region-id:
.. describe:: <region-id>

    Region to display
