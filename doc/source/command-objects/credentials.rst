===========
credentials
===========

Identity v3

credentials create
------------------

.. ''[consider rolling the ec2 creds into this too]''

.. code:: bash

    os credentials create
        --x509
        [<private-key-file>]
        [<certificate-file>]

credentials show
----------------

.. code:: bash

    os credentials show
        [--token]
        [--user]
        [--x509 [--root]]
