================
Interactive Mode
================

OpenStackClient has an interactive mode, similar to the :program:`virsh(1)` or
:program:`lvm(8)` commands on Linux.  This mode is useful for executing a
series of commands without having to reload the CLI, or more importantly,
without having to re-authenticate to the cloud.

Enter interactive mode by issuing the :command:`openstack` command with no
subcommand.  An :code:`(openstack)` prompt will be displayed.  Interactive mode
is terminated with :command:`exit`.

Authentication
==============

Authentication happens exactly as before, using the same global command line
options and environment variables, except it only happens once.
The credentials are cached and re-used for subsequent commands.  This means
that to work with multiple clouds interactive mode must be ended so a
authentication to the second cloud can occur.

Scripting
=========

Using interactive mode inside scripts sounds counter-intuitive, but the same
single-authentication benefit can be achieved by passing OSC commands to
the CLI via :code:`stdin`.

Sample session:

.. code-block:: bash

    # assume auth credentials are in the environment
    $ openstack
    (openstack) keypair list
    +--------+-------------------------------------------------+
    | Name   | Fingerprint                                     |
    +--------+-------------------------------------------------+
    | bunsen | a5:da:0c:52:e8:52:42:a3:4f:b8:22:62:7b:e4:e8:89 |
    | beaker | 45:9c:50:56:7c:fc:3a:b6:b5:60:02:2f:41:fb:a9:4c |
    +--------+-------------------------------------------------+
    (openstack) image list
    +--------------------------------------+----------------+
    | ID                                   | Name           |
    +--------------------------------------+----------------+
    | 78b23835-c800-4d95-9d2a-e4de59a553d8 | OpenWRT r42884 |
    | 2e45d43a-7c25-45f1-b012-06ac313e2f6b | Fedora 20      |
    | de3a8396-3bae-42de-84bd-f4e398b8c320 | CirrOS         |
    +--------------------------------------+----------------+
    (openstack) flavor list
    +--------------------------------------+----------+--------+--------+-----------+------+-------+-------------+-----------+-------------+
    | ID                                   | Name     |    RAM |   Disk | Ephemeral | Swap | VCPUs | RXTX Factor | Is Public | Extra Specs |
    +--------------------------------------+----------+--------+--------+-----------+------+-------+-------------+-----------+-------------+
    | 12594680-56f7-4da2-8322-7266681b3070 | m1.small |   2048 |     20 |         0 |      |     1 |             | True      |             |
    | 9274f903-0cc7-4a95-9124-1968018e355d | m1.tiny  |    512 |      5 |         0 |      |     1 |             | True      |             |
    +--------------------------------------+----------+--------+--------+-----------+------+-------+-------------+-----------+-------------+
    (openstack) server create --image CirrOS --flavor m1.small --key-name beaker sample-server
    +-----------------------------+-------------------------------------------------+
    | Field                       | Value                                           |
    +-----------------------------+-------------------------------------------------+
    | config_drive                |                                                 |
    | created                     | 2014-11-19T18:08:41Z                            |
    | flavor                      | m1.small (12594680-56f7-4da2-8322-7266681b3070) |
    | id                          | 3a9a7f82-e902-4948-9245-52b045c76a1d            |
    | image                       | CirrOS (de3a8396-3bae-42de-84bd-f4e398b8c320)   |
    | key_name                    | bunsen                                          |
    | name                        | sample-server                                   |
    | progress                    | 0                                               |
    | properties                  |                                                 |
    | security_groups             | [{u'name': u'default'}]                         |
    | status                      | BUILD                                           |
    | tenant_id                   | 53c93c7952594d9ba16bd7072a165ce8                |
    | updated                     | 2014-11-19T18:08:42Z                            |
    | user_id                     | 1e4eea54c7124688a8092bec6e2dbee6                |
    +-----------------------------+-------------------------------------------------+

A similar session can be issued all at once:

.. code-block:: bash

    $ openstack <<EOF
    > keypair list
    > flavor show m1.small
    > EOF
    (openstack) +--------+-------------------------------------------------+
    | Name   | Fingerprint                                     |
    +--------+-------------------------------------------------+
    | bunsen | a5:da:0c:52:e8:52:42:a3:4f:b8:22:62:7b:e4:e8:89 |
    | beaker | 45:9c:50:56:7c:fc:3a:b6:b5:60:02:2f:41:fb:a9:4c |
    +--------+-------------------------------------------------+
    (openstack) +----------------------------+--------------------------------------+
    | Field                      | Value                                |
    +----------------------------+--------------------------------------+
    | OS-FLV-DISABLED:disabled   | False                                |
    | OS-FLV-EXT-DATA:ephemeral  | 0                                    |
    | disk                       | 20                                   |
    | id                         | 12594680-56f7-4da2-8322-7266681b3070 |
    | name                       | m1.small                             |
    | os-flavor-access:is_public | True                                 |
    | ram                        | 2048                                 |
    | swap                       |                                      |
    | vcpus                      | 1                                    |
    +----------------------------+--------------------------------------+

Limitations
===========

The obvious limitations to Interactive Mode is that it is not a Domain Specific
Language (DSL), just a simple command processor.  That means there are no variables
or flow control.
