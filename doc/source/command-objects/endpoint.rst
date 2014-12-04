========
endpoint
========

Identity v2, v3

endpoint create
---------------

.. program:: endpoint create
.. code:: bash

    os endpoint create
        --publicurl <public-url>
        [--adminurl <admin-url>]
        [--internalurl <internal-url>]
        [--region <endpoint-region>]
        <service>

endpoint delete
---------------

.. program:: endpoint delete
.. code:: bash

    os endpoint delete
        <endpoint-id>

endpoint list
-------------

.. program:: endpoint list
.. code:: bash

    os endpoint list
        [--long]

endpoint show
-------------

.. program:: endpoint show
.. code:: bash

    os endpoint show
        <endpoint_or_service-type>
