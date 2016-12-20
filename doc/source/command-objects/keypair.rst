=======
keypair
=======

The badly named keypair is really the public key of an OpenSSH key pair to be
used for access to created servers. You can also create a private key for
access to a created server by not passing any argument to the keypair create
command.

Compute v2

keypair create
--------------

Create new public or private key for server ssh access

.. program:: keypair create
.. code:: bash

    openstack keypair create
        [--public-key <file>]
        <name>

.. option:: --public-key <file>

    Filename for public key to add. If not used, creates a private key.

.. describe:: <name>

    New public or private key name

keypair delete
--------------

Delete public or private key(s)

.. program:: keypair delete
.. code:: bash

    openstack keypair delete
        <key> [<key> ...]

.. describe:: <key>

    Name of key(s) to delete (name only)

keypair list
------------

List key fingerprints

.. program:: keypair list
.. code:: bash

    openstack keypair list

keypair show
------------

Display key details

.. program:: keypair show
.. code:: bash

    openstack keypair show
        [--public-key]
        <key>

.. option:: --public-key

    Show only bare public key paired with the generated key

.. describe:: <key>

    Public or private key to display (name only)
