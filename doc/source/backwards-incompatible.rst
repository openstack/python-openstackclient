==============================
Backwards Incompatible Changes
==============================

Despite our best efforts, sometimes the OpenStackClient team may introduce a
backwards incompatible change. For user convenience we are tracking any such
changes here (as of the 1.0.0 release).

Should positional arguments for a command need to change, the OpenStackClient
team attempts to make the transition as painless as possible. Look for
deprecation warnings that indicate the new commands (or options) to use.

Commands labeled as a beta according to :doc:`command-beta` are exempt from
this backwards incompatible change handling.

Backwards Incompatible Changes
==============================

Release 3.0
-----------

1. Remove the ``osc_password`` authentication plugin.

  This was the 'last-resort' plugin default that worked around an old default
  Keystone configuration for the ``admin_endpoint`` and ``public_endpoint``.

  * In favor of: ``password``
  * As of: 3.0
  * Removed in: n/a
  * Bug: n/a
  * Commit: https://review.openstack.org/332938

Releases Before 3.0
-------------------

1. Rename command `openstack project usage list`

  The `project` part of the command was pointless.

  * In favor of: `openstack usage list` instead.
  * As of: 1.0.2
  * Removed in: TBD
  * Bug: https://bugs.launchpad.net/python-openstackclient/+bug/1406654
  * Commit: https://review.openstack.org/#/c/147379/

2. <type> should not be optional for command `openstack service create`

  Previously, the command was `openstack service create <name> --type <type>`,
  whereas now it is: `openstack service create <type> --name <name>`
  This bug also affected python-keystoneclient, and keystone.

  * In favor of: making <type> a positional argument.
  * As of: 1.0.2
  * Removed in: TBD
  * Bug: https://bugs.launchpad.net/python-openstackclient/+bug/1404073
  * Commit: https://review.openstack.org/#/c/143242/

3. Command `openstack security group rule delete` now requires rule id

  Previously, the command was `openstack security group rule delete --proto
  <proto> [--src-ip <ip-address> --dst-port <port-range>] <group>`,
  whereas now it is: `openstack security group rule delete <rule>`.

  * In favor of: Using `openstack security group rule delete <rule>`.
  * As of: 1.2.1
  * Removed in: NA
  * Bug: https://bugs.launchpad.net/python-openstackclient/+bug/1450872
  * Commit: https://review.openstack.org/#/c/179446/

4. Command `openstack image create` does not update already existing image

  Previously, the image create command updated already existing image if it had
  same name. It disabled possibility to create multiple images with same name
  and lead to potentially unwanted update of existing images by image create
  command.
  Now, update code was moved from create action to set action.

  * In favor of: Create multiple images with same name (as glance does).
  * As of: 1.5.0
  * Removed in: NA
  * Bug: https://bugs.launchpad.net/python-openstackclient/+bug/1461817
  * Commit: https://review.openstack.org/#/c/194654/

5. Command `openstack network list --dhcp` has been removed

  The --dhcp option to network list is not a logical use case of listing
  networks, it lists agents.  Another command should be added in the future
  to provide this functionality.  It is highly unlikely anyone uses this
  feature as we don't support any other agent commands.  Use neutron
  dhcp-agent-list-hosting-net command instead.

  * In favor of: Create network agent list command in the future
  * As of: 1.6.0
  * Removed in: NA
  * Bug: https://bugs.launchpad.net/python-openstackclient/+bug/472613
  * Commit: https://review.openstack.org/#/c/194654/

6. Plugin interface change for default API versions

  Previously, the default version was set in the parsed arguments,
  but this makes it impossible to tell what has been passed in at the
  command line, set in an environment variable or is just the default.
  Now, the module should have a DEFAULT_API_VERSION that contains the
  value and it will be set after command line argument, environment
  and OCC file processing.

  * In favor of: DEFAULT_API_VERSION
  * As of: 1.2.1
  * Removed in: NA
  * Bug: https://bugs.launchpad.net/python-openstackclient/+bug/1453229
  * Commit: https://review.openstack.org/#/c/181514/

7. `image set` commands will no longer return the modified resource

  Previously, modifying an image would result in the new image being displayed
  to the user. To keep things consistent with other `set` commands, we will
  no longer be showing the modified resource.

  * In favor of: Use `set` then `show`
  * As of: NA
  * Removed in: NA
  * Bug: NA
  * Commit: NA

8. `region` commands no longer support `url`

  The Keystone team removed support for the `url` attribute from the client
  and server side. Changes to the `create`, `set` and `list` commands for
  regions have been affected.

  * In favor of: NA
  * As of 1.9.0
  * Removed in: NA
  * Bug: https://launchpad.net/bugs/1506841
  * Commit: https://review.openstack.org/#/c/236736/

9. `flavor set/unset` commands will no longer return the modified resource

  Previously, modifying a flavor would result in the new flavor being displayed
  to the user. To keep things consistent with other `set/unset` commands, we
  will no longer be showing the modified resource.

  * In favor of: Use `set/unset` then `show`
  * As of: NA
  * Removed in: NA
  * Bug: https://bugs.launchpad.net/python-openstackclient/+bug/1546065
  * Commit: https://review.openstack.org/#/c/280663/

10. `security group set` commands will no longer return the modified resource

  Previously, modifying a security group would result in the new security group
  being displayed to the user. To keep things consistent with other `set`
  commands, we will no longer be showing the modified resource.

  * In favor of: Use `set` then `show`
  * As of: NA
  * Removed in: NA
  * Bug: https://bugs.launchpad.net/python-openstackclient/+bug/1546065
  * Commit: https://review.openstack.org/#/c/281087/

11. `compute agent set` commands will no longer return the modified resource

  Previously, modifying an agent would result in the new agent being displayed
  to the user. To keep things consistent with other `set` commands, we will
  no longer be showing the modified resource.

  * In favor of: Use `set` then `show`
  * As of: NA
  * Removed in: NA
  * Bug: https://bugs.launchpad.net/python-openstackclient/+bug/1546065
  * Commit: https://review.openstack.org/#/c/281088/

12. <version> <url> <md5hash> should be optional for command `openstack compute agent set`

  Previously, the command was `openstack compute agent set <id> <version> <url> <md5hash>`,
  whereas now it is: `openstack compute agent set <id> --version <version>
                                                       --url <url>
                                                       --md5hash <md5hash>`.

  * In favor of: making <version> <url> <md5hash> optional.
  * As of: NA
  * Removed in: NA
  * Bug: NA
  * Commit: https://review.openstack.org/#/c/328819/

13. `aggregate set` commands will no longer return the modified resource

  Previously, modifying an aggregate would result in the new aggregate being
  displayed to the user. To keep things consistent with other `set` commands,
  we will no longer be showing the modified resource.

  * In favor of: Use `set` then `show`
  * As of: NA
  * Removed in: NA
  * Bug: https://bugs.launchpad.net/python-openstackclient/+bug/1546065
  * Commit: https://review.openstack.org/#/c/281089/

14. Output of `ip floating list` command has changed.

  When using Compute v2, the original output is:

  .. code-block:: bash

      # ip floating list

      +----+--------+------------+----------+-------------+
      | ID | Pool   | IP         | Fixed IP | Instance ID |
      +----+--------+-----------------------+-------------+
      |  1 | public | 172.24.4.1 | None     | None        |
      +----+--------+------------+----------+-------------+

  Now it changes to:

  .. code-block:: bash

      # ip floating list

      +----+---------------------+------------------+-----------+--------+
      | ID | Floating IP Address | Fixed IP Address | Server ID | Pool   |
      +----+---------------------+------------------+-----------+--------+
      |  1 | 172.24.4.1          | None             | None      | public |
      +----+---------------------+------------------+-----------+--------+

  When using Network v2, which is different from Compute v2. The output is:

  .. code-block:: bash

      # ip floating list

      +--------------------------------------+---------------------+------------------+------+
      | ID                                   | Floating IP Address | Fixed IP Address | Port |
      +--------------------------------------+---------------------+------------------+------+
      | 1976df86-e66a-4f96-81bd-c6ffee6407f1 | 172.24.4.3          | None             | None |
      +--------------------------------------+---------------------+------------------+------+

  * In favor of: Use `ip floating list` command
  * As of: NA
  * Removed in: NA
  * Bug: https://bugs.launchpad.net/python-openstackclient/+bug/1519502
  * Commit: https://review.openstack.org/#/c/277720/

For Developers
==============

If introducing a backwards incompatible change, then add the tag:
``BackwardsIncompatibleImpact`` to your git commit message, and if possible,
update this file.

To review all changes that are affected, use the following query:

https://review.openstack.org/#/q/project:openstack/python-openstackclient+AND+message:BackwardsIncompatibleImpact,n,z
