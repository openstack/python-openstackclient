==============================
Backwards Incompatible Changes
==============================

Despite our best efforts, sometimes the OpenStackClient team may introduce a
backwards incompatible change. For user convenience we are tracking any such
changes here (as of the 1.0.0 release).

Should positional arguments for a command need to change, the OpenStackClient
team attempts to make the transition as painless as possible. Look for
deprecation warnings that indicate the new commands (or options) to use.

List of Backwards Incompatible Changes
======================================

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

For Developers
==============

If introducing a backwards incompatible change, then add the tag:
``BackwardsIncompatibleImpact`` to your git commit message, and if possible,
update this file.

To review all changes that are affected, use the following query:

https://review.openstack.org/#/q/project:openstack/python-openstackclient+AND+message:BackwardsIncompatibleImpact,n,z
