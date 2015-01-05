===========
volume type
===========

Volume v1

volume type create
------------------

Create new volume type

.. program:: volume type create
.. code:: bash

    os volume type create
        [--property <key=value> [...] ]
        <name>

.. option:: --property <key=value>

    Set a property on this volume type (repeat option to set multiple properties)

.. describe:: <name>

    New volume type name

volume type delete
------------------

Delete volume type

.. program:: volume type delete
.. code:: bash

    os volume type delete
        <volume-type>

.. describe:: <volume-type>

    Volume type to delete (name or ID)

volume type list
----------------

List volume types

.. program:: volume type list
.. code:: bash

    os volume type list
        [--long]

.. option:: --long

    List additional fields in output

volume type set
---------------

Set volume type properties

.. program:: volume type set
.. code:: bash

    os volume type set
        [--property <key=value> [...] ]
        <volume-type>

.. option:: --property <key=value>

    Property to add or modify for this volume type (repeat option to set multiple properties)

.. describe:: <volume-type>

    Volume type to modify (name or ID)

volume type unset
-----------------

Unset volume type properties

.. program:: volume type unset
.. code:: bash

    os volume type unset
        [--property <key>]
        <volume-type>

.. option:: --property <key>

    Property to remove from volume type (repeat option to remove multiple properties)

.. describe:: <volume-type>

    Volume type to modify (name or ID)
