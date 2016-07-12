=======
mapping
=======

Identity v3

`Requires: OS-FEDERATION extension`

mapping create
--------------

Create new mapping

.. program:: mapping create
.. code:: bash

    os mapping create
        --rules <filename>
        <name>

.. option:: --rules <filename>

    Filename that contains a set of mapping rules (required)

.. _mapping_create-mapping:
.. describe:: <name>

    New mapping name (must be unique)

mapping delete
--------------

Delete mapping(s)

.. program:: mapping delete
.. code:: bash

    os mapping delete
        <mapping> [<mapping> ...]

.. _mapping_delete-mapping:
.. describe:: <mapping>

    Mapping(s) to delete

mapping list
------------

List mappings

.. program:: mapping list
.. code:: bash

    os mapping list

mapping set
-----------

Set mapping properties

.. program:: mapping set
.. code:: bash

    os mapping set
        [--rules <filename>]
        <mapping>

.. option:: --rules <filename>

    Filename that contains a new set of mapping rules

.. _mapping_set-mapping:
.. describe:: <mapping>

    Mapping to modify

mapping show
------------

Display mapping details

.. program:: mapping show
.. code:: bash

    os mapping show
        <mapping>

.. _mapping_show-mapping:
.. describe:: <mapping>

    Mapping to display
