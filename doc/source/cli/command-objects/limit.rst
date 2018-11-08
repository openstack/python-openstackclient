=====
limit
=====

Identity v3

Limits are used to specify project-specific limits thresholds of resources.

limit create
------------

Create a new limit

.. program:: limit create
.. code:: bash

    openstack limit create
        [--description <description>]
        [--region <region>]
        --project <project>
        --service <service>
        --resource-limit <resource-limit>
        <resource-name>

.. option:: --description <description>

   Useful description of the limit or its purpose

.. option:: --region <region>

   Region that the limit should be applied to

.. describe:: --project <project>

   The project that the limit applies to (required)

.. describe:: --service <service>

   The service that is responsible for the resource being limited (required)

.. describe:: --resource-limit <resource-limit>

   The limit to apply to the project (required)

.. describe:: <resource-name>

   The name of the resource to limit (e.g. cores or volumes)

limit delete
------------

Delete project-specific limit(s)

.. program:: limit delete
.. code:: bash

    openstack limit delete
        <limit-id> [<limit-id> ...]

.. describe:: <limit-id>

    Limit(s) to delete (ID)

limit list
----------

List project-specific limits

.. program:: limit list
.. code:: bash

    openstack limit list
        [--service <service>]
        [--resource-name <resource-name>]
        [--region <region>]
        [--project <project>]

.. option:: --service <service>

    The service to filter the response by (name or ID)

.. option:: --resource-name <resource-name>

    The name of the resource to filter the response by

.. option:: --region <region>

   The region name to filter the response by

.. option:: --project <project>

   List resource limits associated with project

limit show
----------

Display details about a limit

.. program:: limit show
.. code:: bash

    openstack limit show
        <limit-id>

.. describe:: <limit-id>

   Limit to display (ID)

limit set
---------

Update a limit

.. program:: limit show
.. code:: bash

    openstack limit set
        [--description <description>]
        [--resource-limit <resource-limit>]
        <limit-id>


.. option:: --description <description>

   Useful description of the limit or its purpose

.. option:: --resource-limit <resource-limit>

   The limit to apply to the project

.. describe:: <limit-id>

   Limit to update (ID)
