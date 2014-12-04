======
region
======

Identity v3

region create
-------------

Create new region

.. code:: bash

    os region create
        [--parent-region <region-id>]
        [--description <region-description>]
        [--url <region-url>]
        <region-id>

:option:`--parent-region` <region-id>
    Parent region

:option:`--description` <region-description>
    New region description

:option:`--url` <region-url>
    New region URL

:option:`<region-id>`
    New region ID

region delete
-------------

Delete region

.. code:: bash

    os region delete
        <region>

:option:`<region>`
    Region to delete

region list
-----------

List regions

.. code:: bash

    os region list
        [--parent-region <region-id>]

:option:`--parent-region` <region-id>
    Filter by a specific parent region

region set
----------

Set region properties

.. code:: bash

    os region set
        [--parent-region <region-id>]
        [--description <region-description>]
        [--url <region-url>]
        <region>

:option:`--parent-region` <region-id>
    New parent region

:option:`--description` <region-description>
    New region description

:option:`--url` <region-url>
    New region URL

:option:`<region>`
    Region ID to modify

region show
-----------

Show region

.. code:: bash

    os region show
    <region>

:option:`<region>`
    Region ID to modify
