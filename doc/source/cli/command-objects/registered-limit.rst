================
registered limit
================

Identity v3

Registered limits are used to define default limits for resources within a
deployment.

registered limit create
-----------------------

Create a new registered limit

.. program:: registered limit create
.. code:: bash

    openstack registered limit create
        [--description <description>]
        [--region <region>]
        --service <service>
        --default-limit <default-limit>
        <resource-name>

.. option:: --description <description>

   Useful description of the registered limit or its purpose

.. option:: --region <region>

   Region that the limit should be applied to

.. describe:: --service  <service>

   The service that is responsible for the resource being limited (required)

.. describe:: --default-limit <default-limit>

   The default limit for projects to assume unless explicitly overridden
   (required)

.. describe:: <resource-name>

   The name of the resource to limit (e.g. cores or volumes)

registered limit delete
-----------------------

Delete registered limit(s)

.. program:: registered limit delete
.. code:: bash

    openstack registered limit delete
        <registered-limit-id> [<registered-limit-id> ...]


.. describe:: <registered-limit-id>

    Registered limit(s) to delete (ID)

registered limit list
---------------------

List registered limits

.. program:: registered limit list
.. code:: bash

    openstack registered limit list
        [--service <service>]
        [--resource-name <resource-name>]
        [--region <region>]

.. option:: --service <service>

    The service to filter the response by (name or ID)

.. option:: --resource-name <resource-name>

    The name of the resource to filter the response by

.. option:: --region <region>

   The region name to filter the response by

registered limit show
---------------------

Display details about a registered limit

.. program:: registered limit show
.. code:: bash

    openstack registered limit show
        <registered-limit-id>

.. describe:: <registered-limit-id>

    Registered limit to display (ID)

registered limit set
--------------------

Update a registered limit

.. program:: registered limit set
.. code:: bash

    openstack registered limit set
        [--service <service>]
        [--resource-name <resource-name>]
        [--default-limit <default-limit>]
        [--description <description>]
        [--region <region>]
        <registered-limit-id>

.. option:: --service <service>

    The service of the registered limit to update (ID or name)

.. option:: --resource-name <resource-name>

    The name of the resource for the limit

.. option:: --default-limit <default-limit>

    The default limit for projects to assume for a given resource

.. option:: --description <description>

    A useful description of the limit or its purpose

.. option:: --region <region>

    The region the limit should apply to

.. describe:: <registered-limit-id>

    Registered limit to display (ID)
