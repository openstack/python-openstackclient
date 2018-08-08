===========
floating ip
===========

Compute v2, Network v2

floating ip create
------------------

Create floating IP

.. program:: floating ip create
.. code:: bash

    openstack floating ip create
        [--subnet <subnet>]
        [--port <port>]
        [--floating-ip-address <ip-address>]
        [--fixed-ip-address <ip-address>]
        [--description <description>]
        [--qos-policy <qos-policy>]
        [--project <project> [--project-domain <project-domain>]]
        [--tag <tag> | --no-tag]
        [--dns-domain <dns-domain>]
        [--dns-name <dns-name>]
        <network>

.. option:: --subnet <subnet>

    Subnet on which you want to create the floating IP (name or ID)
    *Network version 2 only*

.. option:: --port <port>

    Port to be associated with the floating IP (name or ID)
    *Network version 2 only*

.. option:: --floating-ip-address <ip-address>

    Floating IP address
    *Network version 2 only*

.. option:: --fixed-ip-address <ip-address>

    Fixed IP address mapped to the floating IP
    *Network version 2 only*

.. option:: --description <description>

    Set floating IP description
    *Network version 2 only*

.. option:: --qos-policy <qos-policy>

    QoS policy to attach to the floating IP (name or ID)

    *Network version 2 only*

.. option:: --project <project>

    Owner's project (name or ID)

    *Network version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    *Network version 2 only*

.. option:: --tag <tag>

    Tag to be added to the floating IP (repeat option to set multiple tags)

    *Network version 2 only*

.. option:: --no-tag

    No tags associated with the floating IP

    *Network version 2 only*

.. option:: --dns-domain <dns-domain>

    Set DNS domain for this floating IP (requires DNS integration extension).

.. option:: --dns-name <dns-name>

    Set DNS name for this floating IP (requires DNS integration extension).

.. describe:: <network>

    Network to allocate floating IP from (name or ID)

floating ip delete
------------------

Delete floating IP(s)

.. program:: floating ip delete
.. code:: bash

    openstack floating ip delete <floating-ip> [<floating-ip> ...]

.. describe:: <floating-ip>

    Floating IP(s) to delete (IP address or ID)

floating ip list
----------------

List floating IP(s)

.. program:: floating ip list
.. code:: bash

    openstack floating ip list
        [--network <network>]
        [--port <port>]
        [--fixed-ip-address <ip-address>]
        [--long]
        [--status <status>]
        [--project <project> [--project-domain <project-domain>]]
        [--router <router>]
        [--tags <tag>[,<tag>,...]] [--any-tags <tag>[,<tag>,...]]
        [--not-tags <tag>[,<tag>,...]] [--not-any-tags <tag>[,<tag>,...]]

.. option:: --network <network>

    List floating IP(s) according to given network (name or ID)

    *Network version 2 only*

.. option:: --port <port>

    List floating IP(s) according to given port (name or ID)

    *Network version 2 only*

.. option:: --fixed-ip-address <ip-address>

    List floating IP(s) according to given fixed IP address

    *Network version 2 only*

.. option:: --long

    List additional fields in output

    *Network version 2 only*

.. option:: --status <status>

    List floating IP(s) according to given status ('ACTIVE', 'DOWN')

    *Network version 2 only*

.. option:: --project <project>

    List floating IP(s) according to given project (name or ID)

    *Network version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID). This can
    be used in case collisions between project names exist.

    *Network version 2 only*

.. option:: --router <router>

    List floating IP(s) according to given router (name or ID)

    *Network version 2 only*

.. option:: --tags <tag>[,<tag>,...]

    List floating IP(s) which have all given tag(s)

    *Network version 2 only*

.. option:: --any-tags <tag>[,<tag>,...]

    List floating IP(s) which have any given tag(s)

    *Network version 2 only*

.. option:: --not-tags <tag>[,<tag>,...]

    Exclude floating IP(s) which have all given tag(s)

    *Network version 2 only*

.. option:: --not-any-tags <tag>[,<tag>,...]

    Exclude floating IP(s) which have any given tag(s)

    *Network version 2 only*

floating ip set
---------------

Set floating IP properties

.. program:: floating ip set
.. code:: bash

    openstack floating ip set
        [--port <port>]
        [--fixed-ip-address <ip-address>]
        [--qos-policy <qos-policy> | --no-qos-policy]
        [--tag <tag>] [--no-tag]
        <floating-ip>

.. option:: --port <port>

    Associate the floating IP with port (name or ID)

.. option:: --fixed-ip-address <ip-address>

    Fixed IP of the port (required only if port has multiple IPs)

.. option:: --qos-policy <qos-policy>

    Attach QoS policy to the floating IP (name or ID)

.. option:: --no-qos-policy

    Remove the QoS policy attached to the floating IP

.. option:: --tag <tag>

    Tag to be added to the floating IP (repeat option to set multiple tags)

.. option:: --no-tag

    Clear tags associated with the floating IP. Specify both --tag
    and --no-tag to overwrite current tags

.. _floating_ip_set-floating-ip:
.. describe:: <floating-ip>

    Floating IP to associate (IP address or ID)

floating ip show
----------------

Display floating IP details

.. program:: floating ip show
.. code:: bash

    openstack floating ip show <floating-ip>

.. describe:: <floating-ip>

    Floating IP to display (IP address or ID)

floating ip unset
-----------------

Unset floating IP Properties

.. program:: floating ip unset
.. code:: bash

    openstack floating ip unset
        [--port]
        [--qos-policy]
        [--tag <tag> | --all-tag]
        <floating-ip>

.. option:: --port

    Disassociate any port associated with the floating IP

.. option:: --qos-policy

    Remove the QoS policy attached to the floating IP

.. option:: --tag <tag>

    Tag to be removed from the floating IP
    (repeat option to remove multiple tags)

.. option:: --all-tag

    Clear all tags associated with the floating IP

.. _floating_ip_unset-floating-ip:
.. describe:: <floating-ip>

    Floating IP to disassociate (IP address or ID)
