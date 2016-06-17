====
user
====

Identity v2, v3

user create
-----------

Create new user

.. program:: user create
.. code:: bash

    os user create
        [--domain <domain>]
        [--project <project> [--project-domain <project-domain>]]
        [--password <password>]
        [--password-prompt]
        [--email <email-address>]
        [--description <description>]
        [--enable | --disable]
        [--or-show]
        <user-name>

.. option:: --domain <domain>

    Default domain (name or ID)

    .. versionadded:: 3

.. option:: --project <project>

    Default project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --password <password>

    Set user password

.. option:: --password-prompt

    Prompt interactively for password

.. option:: --email <email-address>

    Set user email address

.. option:: --description <description>

    User description

    .. versionadded:: 3

.. option:: --enable

    Enable user (default)

.. option:: --disable

    Disable user

.. option:: --or-show

    Return existing user

    If the username already exist return the existing user data and do not fail.

.. describe:: <user-name>

    New user name

user delete
-----------

Delete user(s)

.. program:: user delete
.. code:: bash

    os user delete
        [--domain <domain>]
        <user> [<user> ...]

.. option:: --domain <domain>

    Domain owning :ref:`\<user\> <user_delete-user>` (name or ID)

    .. versionadded:: 3

.. _user_delete-user:
.. describe:: <user>

    User(s) to delete (name or ID)

user list
---------

List users

.. program:: user list
.. code:: bash

    os user list
        [--project <project>]
        [--domain <domain>]
        [--group <group> | --project <project>]
        [--long]

.. option:: --project <project>

    Filter users by `<project>` (name or ID)

.. option:: --domain <domain>

    Filter users by `<domain>` (name or ID)

    *Identity version 3 only*

.. option:: --group <group>

    Filter users by `<group>` membership (name or ID)

    *Identity version 3 only*

.. option:: --long

    List additional fields in output

user set
--------

Set user properties

.. program:: user set
.. code:: bash

    os user set
        [--name <name>]
        [--project <project> [--project-domain <project-domain>]]
        [--password <password>]
        [--password-prompt]
        [--email <email-address>]
        [--description <description>]
        [--enable|--disable]
        <user>

.. option:: --name <name>

    Set user name

.. option:: --project <project>

    Set default project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --password <password>

    Set user password

.. option:: --password-prompt

    Prompt interactively for password

.. option:: --email <email-address>

    Set user email address

.. option:: --description <description>

    Set user description

    .. versionadded:: 3

.. option:: --enable

    Enable user (default)

.. option:: --disable

    Disable user

.. describe:: <user>

    User to modify (name or ID)

user show
---------

Display user details

.. program:: user show
.. code:: bash

    os user show
        [--domain <domain>]
        <user>

.. option:: --domain <domain>

    Domain owning :ref:`\<user\> <user_show-user>` (name or ID)

    .. versionadded:: 3

.. _user_show-user:
.. describe:: <user>

    User to display (name or ID)
