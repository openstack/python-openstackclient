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

For Developers
==============

If introducing a backwards incompatible change, then add the tag:
``BackwardsIncompatibleImpact`` to your git commit message, and if possible,
update this file.

To review all changes that are affected, use the following query:

https://review.openstack.org/#/q/project:openstack/python-openstackclient+AND+message:BackwardsIncompatibleImpact,n,z
