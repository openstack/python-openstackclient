=========
extension
=========

Many OpenStack server APIs include API extensions that enable
additional functionality.

extension list
--------------

List API extensions

.. program:: extension list
.. code:: bash

    os extension list
        [--compute]
        [--identity]
        [--network]
        [--volume]
        [--long]

.. option:: --compute

    List extensions for the Compute API

.. option:: --identity

    List extensions for the Identity API

.. option:: --network

    List extensions for the Network API

.. option:: --volume

    List extensions for the Block Storage API

.. option:: --long

    List additional fields in output
