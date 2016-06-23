========
endpoint
========

Identity v2, v3

endpoint create
---------------

Create new endpoint

*Identity version 2 only*

.. program:: endpoint create
.. code:: bash

    os endpoint create
        --publicurl <url>
        [--adminurl <url>]
        [--internalurl <url>]
        [--region <region-id>]
        <service>

.. option:: --publicurl <url>

    New endpoint public URL (required)

.. option:: --adminurl <url>

    New endpoint admin URL

.. option:: --internalurl <url>

    New endpoint internal URL

.. option:: --region <region-id>

    New endpoint region ID

.. _endpoint_create-endpoint:
.. describe:: <service>

    Service to be associated with new endpoint (name or ID)

*Identity version 3 only*

.. program:: endpoint create
.. code:: bash

    os endpoint create
        [--region <region-id>]
        [--enable | --disable]
        <service>
        <interface>
        <url>

.. option:: --region <region-id>

    New endpoint region ID

.. option:: --enable

    Enable endpoint (default)

.. option:: --disable

    Disable endpoint

.. describe:: <service>

    Service to be associated with new endpoint(name or ID)

.. describe:: <interface>

    New endpoint interface type (admin, public or internal)

.. describe:: <url>

    New endpoint URL

endpoint delete
---------------

Delete endpoint(s)

.. program:: endpoint delete
.. code:: bash

    os endpoint delete
        <endpoint-id> [<endpoint-id> ...]

.. _endpoint_delete-endpoint:
.. describe:: <endpoint-id>

    Endpoint(s) to delete (ID only)

endpoint list
-------------

List endpoints

.. program:: endpoint list
.. code:: bash

    os endpoint list
        [--service <service]
        [--interface <interface>]
        [--region <region-id>]
        [--long]

.. option:: --service <service>

    Filter by service (name or ID)

    *Identity version 3 only*

.. option:: --interface <interface>

    Filter by interface type (admin, public or internal)

    *Identity version 3 only*

.. option:: --region <region-id>

    Filter by region ID

    *Identity version 3 only*

.. option:: --long

    List additional fields in output

    *Identity version 2 only*

endpoint set
------------

Set endpoint properties

*Identity version 3 only*

.. program:: endpoint set
.. code:: bash

    os endpoint set
        [--region <region-id>]
        [--interface <interface>]
        [--url <url>]
        [--service <service>]
        [--enable | --disable]
        <endpoint-id>

.. option:: --region <region-id>

    New endpoint region ID

.. option:: --interface <interface>

    New endpoint interface type (admin, public or internal)

.. option:: --url <url>

    New endpoint URL

.. option:: --service <service>

    New endpoint service (name or ID)

.. option:: --enable

    Enable endpoint

.. option:: --disable

    Disable endpoint

.. _endpoint_set-endpoint:
.. describe:: <endpoint-id>

    Endpoint to modify (ID only)

endpoint show
-------------

Display endpoint details

.. program:: endpoint show
.. code:: bash

    os endpoint show
        <endpoint>

.. _endpoint_show-endpoint:
.. describe:: <endpoint>

    Endpoint to display (endpoint ID, service ID, service name, service type)
