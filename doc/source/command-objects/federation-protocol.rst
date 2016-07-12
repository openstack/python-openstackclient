===================
federation protocol
===================

Identity v3

`Requires: OS-FEDERATION extension`

federation protocol create
--------------------------

Create new federation protocol

.. program:: federation protocol create
.. code:: bash

    os federation protocol create
        --identity-provider <identity-provider>
        --mapping <mapping>
        <name>

.. option:: --identity-provider <identity-provider>

    Identity provider that will support the new federation protocol (name or ID) (required)

.. option:: --mapping <mapping>

    Mapping that is to be used (name or ID) (required)

.. describe:: <name>

    New federation protocol name (must be unique per identity provider)

federation protocol delete
--------------------------

Delete federation protocol(s)

.. program:: federation protocol delete
.. code:: bash

    os federation protocol delete
        --identity-provider <identity-provider>
        <federation-protocol> [<federation-protocol> ...]

.. option:: --identity-provider <identity-provider>

    Identity provider that supports <federation-protocol> (name or ID) (required)

.. describe:: <federation-protocol>

    Federation protocol(s) to delete (name or ID)

federation protocol list
------------------------

List federation protocols

.. program:: federation protocol list
.. code:: bash

    os federation protocol list
        --identity-provider <identity-provider>

.. option:: --identity-provider <identity-provider>

    Identity provider to list (name or ID) (required)

federation protocol set
-----------------------

Set federation protocol properties

.. program:: federation protocol set
.. code:: bash

    os federation protocol set
        --identity-provider <identity-provider>
        [--mapping <mapping>]
        <federation-protocol>

.. option:: --identity-provider <identity-provider>

    Identity provider that supports <federation-protocol> (name or ID) (required)

.. option:: --mapping <mapping>

    Mapping that is to be used (name or ID)

.. describe:: <federation-protocol>

    Federation protocol to modify (name or ID)

federation protocol show
------------------------

Display federation protocol details

.. program:: federation protocol show
.. code:: bash

    os federation protocol show
        --identity-provider <identity-provider>
        <federation-protocol>

.. option:: --identity-provider <identity-provider>

    Identity provider that supports <federation-protocol> (name or ID) (required)

.. describe:: <federation-protocol>

    Federation protocol to display (name or ID)
