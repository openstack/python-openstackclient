===========
volume type
===========

Block Storage v1, v2

volume type create
------------------

Create new volume type

.. program:: volume type create
.. code:: bash

    os volume type create
        [--description <description>]
        [--public | --private]
        [--property <key=value> [...] ]
        [--project <project>]
        [--project-domain <project-domain>]
        <name>

.. option:: --description <description>

    Volume type description

    .. versionadded:: 2

.. option:: --public

    Volume type is accessible to the public

    .. versionadded:: 2

.. option:: --private

    Volume type is not accessible to the public

    .. versionadded:: 2

.. option:: --property <key=value>

    Set a property on this volume type (repeat option to set multiple properties)

.. option:: --project <project>

    Allow <project> to access private type (name or ID)
    (Must be used with :option:`--private` option)

    *Volume version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    *Volume version 2 only*

.. _volume_type_create-name:
.. describe:: <name>

    Volume type name

volume type delete
------------------

Delete volume type(s)

.. program:: volume type delete
.. code:: bash

    os volume type delete
        <volume-type> [<volume-type> ...]

.. _volume_type_delete-volume-type:
.. describe:: <volume-type>

    Volume type(s) to delete (name or ID)

volume type list
----------------

List volume types

.. program:: volume type list
.. code:: bash

    os volume type list
        [--long]
        [--public | --private]

.. option:: --long

    List additional fields in output

.. option:: --public

    List only public types

    *Volume version 2 only*

.. option:: --private

    List only private types (admin only)

    *Volume version 2 only*

volume type set
---------------

Set volume type properties

.. program:: volume type set
.. code:: bash

    os volume type set
        [--name <name>]
        [--description <description>]
        [--property <key=value> [...] ]
        [--project <project>]
        [--project-domain <project-domain>]
        <volume-type>

.. option:: --name <name>

    Set volume type name

    .. versionadded:: 2

.. option:: --description <description>

    Set volume type description

    .. versionadded:: 2

.. option:: --project <project>

    Set volume type access to project (name or ID) (admin only)

    *Volume version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --property <key=value>

    Set a property on this volume type (repeat option to set multiple properties)

.. _volume_type_set-volume-type:
.. describe:: <volume-type>

    Volume type to modify (name or ID)

volume type show
----------------

Display volume type details

.. program:: volume type show
.. code:: bash

    os volume type show
        <volume-type>

.. _volume_type_show-volume-type:
.. describe:: <volume-type>

    Volume type to display (name or ID)

volume type unset
-----------------

Unset volume type properties

.. program:: volume type unset
.. code:: bash

    os volume type unset
        [--property <key> [...] ]
        [--project <project>]
        [--project-domain <project-domain>]
        <volume-type>

.. option:: --property <key>

    Property to remove from volume type (repeat option to remove multiple properties)

.. option:: --project <project>

    Removes volume type access from project (name or ID) (admin only)

    *Volume version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. _volume_type_unset-volume-type:
.. describe:: <volume-type>

    Volume type to modify (name or ID)
