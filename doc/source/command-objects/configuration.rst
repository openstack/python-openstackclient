=============
configuration
=============

Available for all services

configuration show
------------------

Show the current openstack client configuration.  This command is a little
different from other show commands because it does not take a resource name
or id to show.  The command line options, such as --os-cloud, can be used to
show different configurations.

.. program:: configuration show
.. code:: bash

    os configuration show
        [--mask | --unmask]

.. option:: --mask

    Attempt to mask passwords (default)

.. option:: --unmask

    Show password in clear text
