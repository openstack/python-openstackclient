====
user
====

Identity v2, v3

user create
-----------

Create new user

.. program:: user create
.. code:: bash

    openstack user create
        [--domain <domain>]
        [--project <project> [--project-domain <project-domain>]]
        [--password <password>]
        [--password-prompt]
        [--email <email-address>]
        [--description <description>]
        [--multi-factor-auth-rule <rule>]
        [--ignore-lockout-failure-attempts| --no-ignore-lockout-failure-attempts]
        [--ignore-password-expiry| --no-ignore-password-expiry]
        [--ignore-change-password-upon-first-use| --no-ignore-change-password-upon-first-use]
        [--enable-lock-password| --disable-lock-password]
        [--enable-multi-factor-auth| --disable-multi-factor-auth]
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

.. option:: --ignore-lockout-failure-attempts

    Opt into ignoring the number of times a user has authenticated and
    locking out the user as a result

.. option:: --no-ignore-lockout-failure-attempts

    Opt out of ignoring the number of times a user has authenticated
    and locking out the user as a result

.. option:: --ignore-change-password-upon-first-use

    Control if a user should be forced to change their password immediately
    after they log into keystone for the first time. Opt into ignoring
    the user to change their password during first time login in keystone.

.. option:: --no-ignore-change-password-upon-first-use

    Control if a user should be forced to change their password immediately
    after they log into keystone for the first time. Opt out of ignoring
    the user to change their password during first time login in keystone.

.. option:: --ignore-password-expiry

    Opt into allowing user to continue using passwords that may be
    expired

.. option:: --no-ignore-password-expiry

    Opt out of allowing user to continue using passwords that may be
    expired

.. option:: --enable-lock-password

    Disables the ability for a user to change its password through
    self-service APIs

.. option:: --disable-lock-password

    Enables the ability for a user to change its password through
    self-service APIs

.. option:: --enable-multi-factor-auth

    Enables the MFA (Multi Factor Auth)

.. option:: --disable-multi-factor-auth

    Disables the MFA (Multi Factor Auth)

.. option:: --multi-factor-auth-rule <rule>

    Set multi-factor auth rules. For example, to set a rule requiring the
    "password" and "totp" auth methods to be provided,
    use: "--multi-factor-auth-rule password,totp".
    May be provided multiple times to set different rule combinations.

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

    openstack user delete
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

    openstack user list
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

    openstack user set
        [--name <name>]
        [--project <project> [--project-domain <project-domain>]]
        [--password <password>]
        [--password-prompt]
        [--email <email-address>]
        [--description <description>]
        [--multi-factor-auth-rule <rule>]
        [--ignore-lockout-failure-attempts| --no-ignore-lockout-failure-attempts]
        [--ignore-password-expiry| --no-ignore-password-expiry]
        [--ignore-change-password-upon-first-use| --no-ignore-change-password-upon-first-use]
        [--enable-lock-password| --disable-lock-password]
        [--enable-multi-factor-auth| --disable-multi-factor-auth]
        [--enable|--disable]
        <user>

.. option:: --name <name>

    Set user name

.. option:: --domain <domain>

    Domain the user belongs to (name or ID).
    This can be used in case collisions between user names exist.

    .. versionadded:: 3

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

.. option:: --ignore-lockout-failure-attempts

    Opt into ignoring the number of times a user has authenticated and
    locking out the user as a result

.. option:: --no-ignore-lockout-failure-attempts

    Opt out of ignoring the number of times a user has authenticated
    and locking out the user as a result

.. option:: --ignore-change-password-upon-first-use

    Control if a user should be forced to change their password immediately
    after they log into keystone for the first time. Opt into ignoring
    the user to change their password during first time login in keystone.

.. option:: --no-ignore-change-password-upon-first-use

    Control if a user should be forced to change their password immediately
    after they log into keystone for the first time. Opt out of ignoring
    the user to change their password during first time login in keystone.

.. option:: --ignore-password-expiry

    Opt into allowing user to continue using passwords that may be
    expired

.. option:: --no-ignore-password-expiry

    Opt out of allowing user to continue using passwords that may be
    expired

.. option:: --enable-lock-password

    Disables the ability for a user to change its password through
    self-service APIs

.. option:: --disable-lock-password

    Enables the ability for a user to change its password through
    self-service APIs

.. option:: --enable-multi-factor-auth

    Enables the MFA (Multi Factor Auth)

.. option:: --disable-multi-factor-auth

    Disables the MFA (Multi Factor Auth)

.. option:: --multi-factor-auth-rule <rule>

    Set multi-factor auth rules. For example, to set a rule requiring the
    "password" and "totp" auth methods to be provided,
    use: "--multi-factor-auth-rule password,totp".
    May be provided multiple times to set different rule combinations.

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

    openstack user show
        [--domain <domain>]
        <user>

.. option:: --domain <domain>

    Domain owning :ref:`\<user\> <user_show-user>` (name or ID)

    .. versionadded:: 3

.. _user_show-user:
.. describe:: <user>

    User to display (name or ID)
