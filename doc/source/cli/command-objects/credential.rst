==========
credential
==========

Identity v3

credential create
-----------------

Create new credential

.. program:: credential create
.. code:: bash

    openstack credential create
        [--type <type>]
        [--project <project>]
        <user> <data>

.. option:: --type <type>

    New credential type

.. option:: --project <project>

    Project which limits the scope of the credential (name or ID)

.. _credential_create:
.. describe:: <user>

    User that owns the credential (name or ID)

.. describe:: <data>

    New credential data

credential delete
-----------------

Delete credential(s)

.. program:: credential delete
.. code:: bash

    openstack credential delete
        <credential-id> [<credential-id> ...]

.. _credential_delete:
.. describe:: <credential-id>

    ID(s) of credential to delete

credential list
---------------

List credentials

.. program:: credential list
.. code:: bash

    openstack credential list

credential set
--------------

Set credential properties

.. program:: credential set
.. code:: bash

    openstack credential set
        [--user <user>]
        [--type <type>]
        [--data <data>]
        [--project <project>]
        <credential-id>

.. option:: --user <user>

    User that owns the credential (name or ID)

.. option:: --type <type>

    New credential type

.. option:: --data <data>

    New credential data

.. option:: --project <project>

    Project which limits the scope of the credential (name or ID)

.. _credential_set:
.. describe:: <credential-id>

    ID of credential to change

credential show
---------------

Display credential details

.. program:: credential show
.. code:: bash

    openstack credential show
        <credential-id>

.. _credential_show:
.. describe:: <credential-id>

    ID of credential to display
