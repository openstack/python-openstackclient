=======
service
=======

Identity v2, v3

service create
--------------

Create new service

.. program:: service create
.. code-block:: bash

    os service create
        [--name <name>]
        [--description <description>]
        [--enable | --disable]
        <type>

.. option:: --name <name>

    New service name

.. option:: --description <description>

    New service description

.. option:: --enable

    Enable service (default)

    *Identity version 3 only*

.. option:: --disable

    Disable service

    *Identity version 3 only*

.. _service_create-type:
.. describe:: <type>

    New service type (compute, image, identity, volume, etc)

service delete
--------------

Delete service(s)

.. program:: service delete
.. code-block:: bash

    os service delete
        <service> [<service> ...]

.. _service_delete-type:
.. describe:: <service>

    Service(s) to delete (type, name or ID)

service list
------------

List services

.. program:: service list
.. code-block:: bash

    os service list
        [--long]

.. option:: --long

    List additional fields in output

Returns service fields ID, Name and Type. :option:`--long` adds Description
and Enabled (*Identity version 3 only*) to the output.

service set
-----------

Set service properties

* Identity version 3 only*

.. program:: service set
.. code-block:: bash

    os service set
        [--type <type>]
        [--name <name>]
        [--description <description>]
        [--enable | --disable]
        <service>

.. option:: --type <type>

    New service type (compute, image, identity, volume, etc)

.. option:: --name <name>

    New service name

.. option:: --description <description>

    New service description

.. option:: --enable

    Enable service

.. option:: --disable

    Disable service

.. _service_set-service:
.. describe:: <service>

    Service to modify (type, name or ID)

service show
------------

Display service details

.. program:: service show
.. code-block:: bash

    os service show
        [--catalog]
        <service>

.. option:: --catalog

    Show service catalog information

    *Identity version 2 only*

.. _service_show-service:
.. describe:: <service>

    Service to display (type, name or ID)
