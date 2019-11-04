=======
keypair
=======

The badly named keypair is really the public key of an OpenSSH key pair to be
used for access to created servers. You can also create a private key for
access to a created server by not passing any argument to the keypair create
command.

Compute v2

.. autoprogram-cliff:: openstack.compute.v2
   :command: keypair *
