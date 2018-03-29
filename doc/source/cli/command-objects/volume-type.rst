===========
volume type
===========

Block Storage v1, v2

volume type create
------------------

Create new volume type

.. program:: volume type create
.. code:: bash

    openstack volume type create
        [--description <description>]
        [--public | --private]
        [--property <key=value> [...] ]
        [--project <project>]
        [--project-domain <project-domain>]
        [--encryption-provider <provider>]
        [--encryption-cipher <cipher>]
        [--encryption-key-size <key-size>]
        [--encryption-control-location <control-location>]
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

.. option:: --encryption-provider <provider>

    Set the encryption provider format for this volume type
    (e.g "luks" or "plain") (admin only)

    This option is required when setting encryption type of a volume.
    Consider using other encryption options such as: :option:`--encryption-cipher`,
    :option:`--encryption-key-size` and :option:`--encryption-control-location`

.. option:: --encryption-cipher <cipher>

    Set the encryption algorithm or mode for this volume type
    (e.g "aes-xts-plain64") (admin only)

.. option:: --encryption-key-size <key-size>

    Set the size of the encryption key of this volume type
    (e.g "128" or "256") (admin only)

.. option:: --encryption-control-location <control-location>

    Set the notional service where the encryption is performed
    ("front-end" or "back-end") (admin only)

    The default value for this option is "front-end" when setting encryption type of
    a volume. Consider using other encryption options such as: :option:`--encryption-cipher`,
    :option:`--encryption-key-size` and :option:`--encryption-provider`

.. _volume_type_create-name:
.. describe:: <name>

    Volume type name

volume type delete
------------------

Delete volume type(s)

.. program:: volume type delete
.. code:: bash

    openstack volume type delete
        <volume-type> [<volume-type> ...]

.. _volume_type_delete-volume-type:
.. describe:: <volume-type>

    Volume type(s) to delete (name or ID)

volume type list
----------------

List volume types

.. program:: volume type list
.. code:: bash

    openstack volume type list
        [--long]
        [--default | --public | --private]
        [--encryption-type]

.. option:: --long

    List additional fields in output

.. option:: --public

    List only public types

    *Volume version 2 only*

.. option:: --private

    List only private types (admin only)

    *Volume version 2 only*

.. option:: --default

    List the default volume type

    *Volume version 2 only*

.. option:: --encryption-type

    Display encryption information for each volume type (admin only)

volume type set
---------------

Set volume type properties

.. program:: volume type set
.. code:: bash

    openstack volume type set
        [--name <name>]
        [--description <description>]
        [--property <key=value> [...] ]
        [--project <project>]
        [--project-domain <project-domain>]
        [--encryption-provider <provider>]
        [--encryption-cipher <cipher>]
        [--encryption-key-size <key-size>]
        [--encryption-control-location <control-location>]
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

.. option:: --encryption-provider <provider>

    Set the encryption provider format for this volume type
    (e.g "luks" or "plain") (admin only)

    This option is required when setting encryption type of a volume for the first time.
    Consider using other encryption options such as: :option:`--encryption-cipher`,
    :option:`--encryption-key-size` and :option:`--encryption-control-location`

.. option:: --encryption-cipher <cipher>

    Set the encryption algorithm or mode for this volume type
    (e.g "aes-xts-plain64") (admin only)

.. option:: --encryption-key-size <key-size>

    Set the size of the encryption key of this volume type
    (e.g "128" or "256") (admin only)

.. option:: --encryption-control-location <control-location>

    Set the notional service where the encryption is performed
    ("front-end" or "back-end") (admin only)

    The default value for this option is "front-end" when setting encryption type of
    a volume for the first time. Consider using other encryption options such as:
    :option:`--encryption-cipher`, :option:`--encryption-key-size` and :option:`--encryption-provider`

.. _volume_type_set-volume-type:
.. describe:: <volume-type>

    Volume type to modify (name or ID)

volume type show
----------------

Display volume type details

.. program:: volume type show
.. code:: bash

    openstack volume type show
        [--encryption-type]
        <volume-type>

.. option:: --encryption-type

    Display encryption information of this volume type (admin only)

.. _volume_type_show-volume-type:
.. describe:: <volume-type>

    Volume type to display (name or ID)

volume type unset
-----------------

Unset volume type properties

.. program:: volume type unset
.. code:: bash

    openstack volume type unset
        [--property <key> [...] ]
        [--project <project>]
        [--project-domain <project-domain>]
        [--encryption-type]
        <volume-type>

.. option:: --property <key>

    Property to remove from volume type (repeat option to remove multiple properties)

.. option:: --project <project>

    Removes volume type access from project (name or ID) (admin only)

    *Volume version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    *Volume version 2 only*

.. option:: --encryption-type

    Remove the encryption type for this volume type (admin only)

.. _volume_type_unset-volume-type:
.. describe:: <volume-type>

    Volume type to modify (name or ID)
