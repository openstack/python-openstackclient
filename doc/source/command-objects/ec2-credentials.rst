===============
ec2 credentials
===============

Identity v2

ec2 credentials create
----------------------

Create EC2 credentials

.. program:: ec2 credentials create
.. code-block:: bash

    os ec2 credentials create
        [--project <project>]
        [--user <user>]

.. option:: --project <project>

    Specify an alternate project (default: current authenticated project)

.. option:: --user <user>

    Specify an alternate user (default: current authenticated user)

The :option:`--project` and :option:`--user`  options are typically only
useful for admin users, but may be allowed for other users depending on
the policy of the cloud and the roles granted to the user.

ec2 credentials delete
----------------------

Delete EC2 credentials

.. program:: ec2 credentials delete
.. code-block:: bash

    os ec2 credentials delete
        [--user <user>]
        <access-key>

.. option:: --user <user>

    Specify a user

.. _ec2_credentials_delete-access-key:
.. describe:: access-key

    Credentials access key

The :option:`--user` option is typically only useful for admin users, but
may be allowed for other users depending on the policy of the cloud and
the roles granted to the user.

ec2 credentials list
--------------------

List EC2 credentials

.. program:: ec2 credentials list
.. code-block:: bash

    os ec2 credentials list
        [--user <user>]

.. option:: --user <user>

    Filter list by <user>

The :option:`--user` option is typically only useful for admin users, but
may be allowed for other users depending on the policy of the cloud and
the roles granted to the user.

ec2 credentials show
--------------------

Display EC2 credentials details

.. program:: ec2 credentials show
.. code-block:: bash

    os ec2 credentials show
        [--user <user>]
        <access-key>

.. option:: --user <user>

    Specify a user

.. _ec2_credentials_show-access-key:
.. describe:: access-key

    Credentials access key

The :option:`--user` option is typically only useful for admin users, but
may be allowed for other users depending on the policy of the cloud and
the roles granted to the user.
