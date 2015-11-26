====================
object store account
====================

Object Storage v1

object store account set
------------------------

Set account properties

.. program:: object store account set
.. code:: bash

    os object store account set
        [--property <key=value> [...] ]

.. option:: --property <key=value>

    Set a property on this account (repeat option to set multiple properties)

object store account show
-------------------------

Display account details

.. program:: object store account show
.. code:: bash

    os object store account show

object store account unset
--------------------------

Unset account properties

.. program:: object store account unset
.. code:: bash

    os object store account unset
        [--property <key>]

.. option:: --property <key>

    Property to remove from account (repeat option to remove multiple properties)
