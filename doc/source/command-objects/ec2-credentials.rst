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
        [--user-domain <user-domain>]
        [--project-domain <project-domain>]

.. option:: --project <project>

    Create credentials in project (name or ID; default: current authenticated project)

.. option:: --user <user>

    Create credentials for user (name or ID; default: current authenticated user)

.. option:: --user-domain <user-domain>

    Domain the user belongs to (name or ID). This can be
    used in case collisions between user names exist.

    .. versionadded:: 3

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID). This can be
    used in case collisions between user names exist.

    .. versionadded:: 3

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
        [--user-domain <user-domain>]
        <access-key> [<access-key> ...]

.. option:: --user <user>

    Delete credentials for user (name or ID)

.. option:: --user-domain <user-domain>

    Select user from a specific domain (name or ID)
    This can be used in case collisions between user names exist.

    .. versionadded:: 3

.. _ec2_credentials_delete-access-key:
.. describe:: access-key

    Credentials access key(s)

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
        [--user-domain <user-domain>]

.. option:: --user <user>

    Filter list by <user> (name or ID)

.. option:: --user-domain <user-domain>

    Select user from a specific domain (name or ID)
    This can be used in case collisions between user names exist.

    .. versionadded:: 3

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
        [--user-domain <user-domain>]
        <access-key>

.. option:: --user <user>

    Show credentials for user (name or ID)

.. option:: --user-domain <user-domain>

    Select user from a specific domain (name or ID)
    This can be used in case collisions between user names exist.

    .. versionadded:: 3

.. _ec2_credentials_show-access-key:
.. describe:: access-key

    Credentials access key

The :option:`--user` option is typically only useful for admin users, but
may be allowed for other users depending on the policy of the cloud and
the roles granted to the user.
