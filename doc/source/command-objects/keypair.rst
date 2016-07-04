=======
keypair
=======

The badly named keypair is really the public key of an OpenSSH key pair to be
used for access to created servers.

Compute v2

keypair create
--------------

Create new public key

.. program:: keypair create
.. code:: bash

    os keypair create
        [--public-key <file>]
        <name>

.. option:: --public-key <file>

    Filename for public key to add

.. describe:: <name>

    New public key name

keypair delete
--------------

Delete public key(s)

.. program:: keypair delete
.. code:: bash

    os keypair delete
        <key> [<key> ...]

.. describe:: <key>

    Public key(s) to delete (name only)

keypair list
------------

List public key fingerprints

.. program:: keypair list
.. code:: bash

    os keypair list

keypair show
------------

Display public key details

.. program:: keypair show
.. code:: bash

    os keypair show
        [--public-key]
        <key>

.. option:: --public-key

    Show only bare public key (name only)

.. describe:: <key>

    Public key to display (name only)
