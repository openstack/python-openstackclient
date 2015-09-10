=======
account
=======

Object Store v1

account set
-----------

Set account properties

.. program:: account set
.. code:: bash

    os account set
        [--property <key=value> [...] ]

.. option:: --property <key=value>

    Set a property on this account (repeat option to set multiple properties)

account show
------------

Display account details

.. program:: account show
.. code:: bash

    os account show

account unset
-------------

Unset account properties

.. program:: account unset
.. code:: bash

    os account unset
        [--property <key>]

.. option:: --property <key>

    Property to remove from account (repeat option to remove multiple properties)
