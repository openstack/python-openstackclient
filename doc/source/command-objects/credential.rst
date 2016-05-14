===========
credential
===========

Identity v3

credential create
------------------

.. ''[consider rolling the ec2 creds into this too]''

.. code:: bash

    os credential create
        --x509
        [<private-key-file>]
        [<certificate-file>]

credential show
----------------

.. code:: bash

    os credential show
        [--token]
        [--user]
        [--x509 [--root]]
