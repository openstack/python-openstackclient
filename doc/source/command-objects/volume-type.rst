===========
volume type
===========

Volume v1, v2

volume type create
------------------

Create new volume type

.. program:: volume type create
.. code:: bash

    os volume type create
        [--description <description>]
        [--public | --private]
        [--property <key=value> [...] ]
        <name>

.. option:: --description <description>

    New volume type description

    .. versionadded:: 2

.. option:: --public

    Volume type is accessible to the public

    .. versionadded:: 2

.. option:: --private

    Volume type is not accessible to the public

    .. versionadded:: 2

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

*Only supported for Volume API v1*

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

*Only supported for Volume API v1*

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
