=============
Release Notes
=============

1.0.2 (19 Jan 2015)
===================

* The OpenStackClient content from the OpenStack Wiki has been migrated into
  the OSC source repo.  This includes the :doc:`commands`, :doc:`command-list`
  and :doc:`humaninterfaceguide` documents.

* Set a default domain ID when both ``OS_USER_DOMAIN_ID`` and
  ``OS_USER_DOMAIN_NAME`` are not set.  This is also done for
  ``OS_PROJECT_DOMAIN_ID`` and ``OS_PROJECT_DOMAIN_NAME`.
  (*Identity API v3 only*).
  Bug 1385338_: Improve domain related defaults when using v3 identity

* Add new ``usage show`` command to display project resource usage information.
  Bug 1400796_: Quick usage report - nova usage

* Add ``--project`` option to ``user list`` command to filter users by project
  (*Identity API v3 only*).
  Bug 1397251_: allow `openstack user list` to use other filters

* Add ``--user`` to ``project list`` command to filter projects by user
  (*Identity API v3 only*).
  Bug 1394793_: support the keystone api /v3/users/$userid/projects

* Add ``--project`` and ``--user`` options to ``role list`` to filter roles
  by project and/or user.  This makes the v2 command very similar to the
  v3 command.
  (*Identity API v2 only*).
  Bug 1409179_: `user role list` command should be worked into `role list`

* Bug 1390507_: Quota show requires cinder in keystone catalog
* Bug 1400531_: Authentication failure results in useless error message
* Bug 1400597_: delete multiple objects
* Bug 1400795_: No list availability zones option
* Bug 1404073_: type should be required for v2.0 service create
* Bug 1404434_: add missing docs for service command
* Bug 1404931_: volume list does not show attached servers
* Bug 1404997_: Allow description to be set for service create/update
* Bug 1405416_: Compute region selection broken
* Bug 1406654_: Remove deprecated commands from help
* Bug 1406737_: v3 endpoint related commands access service.name without check
* Bug 1408585_: Backup list doesn't show backup's name
* Bug 1410364_: Version discovery fails with default Keystone config
* Bug 1411179_: network client don't use session
* Bug 1411337_: identity v3 service list should have "description" column

.. _1385338: https://bugs.launchpad.net/bugs/1385338
.. _1406654: https://bugs.launchpad.net/bugs/1406654
.. _1411337: https://bugs.launchpad.net/bugs/1411337
.. _1400531: https://bugs.launchpad.net/bugs/1400531
.. _1406737: https://bugs.launchpad.net/bugs/1406737
.. _1409179: https://bugs.launchpad.net/bugs/1409179
.. _1408585: https://bugs.launchpad.net/bugs/1408585
.. _1405416: https://bugs.launchpad.net/bugs/1405416
.. _1404931: https://bugs.launchpad.net/bugs/1404931
.. _1404434: https://bugs.launchpad.net/bugs/1404434
.. _1404073: https://bugs.launchpad.net/bugs/1404073
.. _1400796: https://bugs.launchpad.net/bugs/1400796
.. _1400795: https://bugs.launchpad.net/bugs/1400795
.. _1400597: https://bugs.launchpad.net/bugs/1400597
.. _1397251: https://bugs.launchpad.net/bugs/1397251
.. _1394793: https://bugs.launchpad.net/bugs/1394793
.. _1390507: https://bugs.launchpad.net/bugs/1390507
.. _1410364: https://bugs.launchpad.net/bugs/1410364
.. _1404997: https://bugs.launchpad.net/bugs/1404997
.. _1411179: https://bugs.launchpad.net/bugs/1411179


1.0.1 (08 Dec 2014)
===================

* Bug 1399757_: EC2 credentials create fails

.. _1399757: https://bugs.launchpad.net/bugs/1399757


1.0.0 (04 Dec 2014)
===================

* Bug 1337422_: document different ways to authenticate
* Bug 1383333_: Creating volume from image required image ID
* Bug 1292638_: Perhaps API Versions should Match Easier
* Bug 1390389_: create with a soft fail (create or show) for keystone operations
* Bug 1387932_: add keystone v3 region object
* Bug 1378842_: OSC fails to show server details if booted from volume
* Bug 1383338_: server create problems in boot-from-volume
* Bug 1337685_: Add the ability to list networks extensions
* Bug 1355838_: Don't make calls to Keystone for authN if insufficient args are present
* Bug 1371924_: strings are being treated as numbers
* Bug 1372070_: help text in error on openstack image save
* Bug 1372744_: v3 credential set always needs --user option
* Bug 1376833_: odd behavior when editing the domain of a user through Keystone v3 API
* Bug 1378165_: Domains should be supported for 'user show' command
* Bug 1378565_: The '--domain' arg for identity commands should not require domain lookup
* Bug 1379871_: token issue for identity v3 is broken
* Bug 1383083_: repeated to generate clientmanager in interactive mode
* Added functional tests framework and identity/object tests
* Authentication Plugin Support
* Use keystoneclient.session as the base HTTP transport
* implement swift client commands
* clean up 'links' section in keystone v3 resources
* Add cliff-tablib to requirements
* Include support for using oslo debugger in tests
* Close file handlers that were left open
* Added framework for i18n support, and marked Identity v2.0 files for translation
* Add 'command list' command
* CRUD Support for ``OS-FEDERATION`` resources (protocol, mappings, identity providers)

.. _1337422: https://bugs.launchpad.net/bugs/1337422
.. _1383333: https://bugs.launchpad.net/bugs/1383333
.. _1292638: https://bugs.launchpad.net/bugs/1292638
.. _1390389: https://bugs.launchpad.net/bugs/1390389
.. _1387932: https://bugs.launchpad.net/bugs/1387932
.. _1378842: https://bugs.launchpad.net/bugs/1378842
.. _1383338: https://bugs.launchpad.net/bugs/1383338
.. _1337685: https://bugs.launchpad.net/bugs/1337685
.. _1355838: https://bugs.launchpad.net/bugs/1355838
.. _1371924: https://bugs.launchpad.net/bugs/1371924
.. _1372070: https://bugs.launchpad.net/bugs/1372070
.. _1372744: https://bugs.launchpad.net/bugs/1372744
.. _1376833: https://bugs.launchpad.net/bugs/1376833
.. _1378165: https://bugs.launchpad.net/bugs/1378165
.. _1378565: https://bugs.launchpad.net/bugs/1378565
.. _1379871: https://bugs.launchpad.net/bugs/1379871
.. _1383083: https://bugs.launchpad.net/bugs/1383083


0.4.1 (08 Sep 2014)
===================

* Bug 1319381_: remove insecure keyring support
* Bug 1317478_: fix ``project create`` for domain admin
* Bug 1317485_: fix ``project list`` for domain admins
* Bug 1281888_: add region filter to ``endpoint list`` command
* Bug 1337245_: add ``user password set`` command
* Bug 1337684_: add ``extension list --compute``
* Bug 1337687_: add ``extension list --volume``
* Bug 1343658_: fix ``container list`` command
* Bug 1343659_: add network command help text
* Bug 1348475_: add fields to ``image list`` output
* Bug 1351121_: v3 ``endpoint set`` should not require service option
* Bug 1352119_: v2 ``user create`` response error
* Bug 1353788_: test_file_resource() failure
* Bug 1364540_: load_keyring() exception fixed in bug 1319381_
* Bug 1365505_: domain information not in help output
* fix ``security group list`` for non-admin
* fix ``server add security group``
* add ``container create`` and ``container delete`` commands
* add ``object create`` and ``object delete`` commands
* add initial support for global ``--timing`` options (similar to nova CLI)
* complete Python 3 compatibility
* fix ``server resize`` command
* add authentication via ``--os-trust-id`` for Identity v3
* Add initial support for Network API, ``network create|delete|list|show``

.. _1319381: https://bugs.launchpad.net/bugs/1319381
.. _1317478: https://bugs.launchpad.net/bugs/1317478
.. _1317485: https://bugs.launchpad.net/bugs/1317485
.. _1281888: https://bugs.launchpad.net/bugs/1281888
.. _1337245: https://bugs.launchpad.net/bugs/1337245
.. _1337684: https://bugs.launchpad.net/bugs/1337684
.. _1337687: https://bugs.launchpad.net/bugs/1337687
.. _1343658: https://bugs.launchpad.net/bugs/1343658
.. _1343659: https://bugs.launchpad.net/bugs/1343659
.. _1348475: https://bugs.launchpad.net/bugs/1348475
.. _1351121: https://bugs.launchpad.net/bugs/1351121
.. _1352119: https://bugs.launchpad.net/bugs/1352119
.. _1353788: https://bugs.launchpad.net/bugs/1353788
.. _1364540: https://bugs.launchpad.net/bugs/1364540
.. _1365505: https://bugs.launchpad.net/bugs/1365505


0.4.0 (20 Jun 2014)
===================

* Bug 1184012_: fix Identity v2 endpoint command name/id handling
* Bug 1207615_: add ``--volume`` and ``--force`` to ``image create`` command
* Bug 1220280_: add ``--property`` to project create and set commands
* Bug 1246310_: add ``role assignments list`` command
* Bug 1285800_: rename ``agent`` to ``compute agent``
* Bug 1289513_: add ``--domain`` to project list
* Bug 1289594_: fix keypair show output
* Bug 1292337_: fix ec2 credentials project ID output
* Bug 1303978_: fix output of ``volume type create`` command
* Bug 1316870_: display all output when ``--lines`` omitted from ``console log show`` command
* add 'interface' and 'url' columns to endpoint list command
* add identity provider create/delete/list/set/show commands
* change ``volume create --volume-type`` option to ``--type``
* fix ``server image create`` command output
* configure appropriate logging levels for ``--verbose``, ``--quiet`` and ``--debug``
* properly handle properties in Image v1 ``create`` and ``set`` commands
* rename Identity v2 ``token create`` to ``token issue``
* add Identity v2 ``token revoke`` command
* refactor the ``group|user|role list`` command filters so that each command
  only lists rows of that type of object, ie ``user list`` always lists users, etc.
* add ``role assignment list`` command
* add ``extension list`` command

.. _1184012: https://launchpad.net/bugs/1184012
.. _1207615: https://launchpad.net/bugs/1207615
.. _1220280: https://launchpad.net/bugs/1220280
.. _1246310: https://launchpad.net/bugs/1246310
.. _1285800: https://launchpad.net/bugs/1285800
.. _1289513: https://launchpad.net/bugs/1289513
.. _1289594: https://launchpad.net/bugs/1289594
.. _1292337: https://launchpad.net/bugs/1292337
.. _1303978: https://launchpad.net/bugs/1303978
.. _1316870: https://launchpad.net/bugs/1316870

0.3.1 (28 Feb 2014)
===================

* add ``token create`` command
* internal changes for Python 3.3 compatibility
* Bug 1100116_: Prompt interactive user for passwords in ``user create`` and ``user set``
* Bug 1198171_: add domain support options for Identity v3
* Bug 1241177_: Fix region handling in volume commands
* Bug 1256935_: Clean up ``security group rule list`` output format
* Bug 1269821_: Fix for unreleased Glance client change in internal class structure
* Bug 1284957_: Correctly pass ``--cacert`` and ``--insecure`` to Identity client in token flow auth

.. _1100116: https://bugs.launchpad.net/ubuntu/+source/python-keystoneclient/+bug/1100116
.. _1198171: https://bugs.launchpad.net/keystone/+bug/1198171
.. _1241177: https://bugs.launchpad.net/python-openstackclient/+bug/1241177
.. _1256935: https://bugs.launchpad.net/python-openstackclient/+bug/1256935
.. _1269821: https://bugs.launchpad.net/python-openstackclient/+bug/1269821
.. _1284957: https://bugs.launchpad.net/python-openstackclient/+bug/1284957

0.3.0 (17 Dec 2013)
===================

* add new command plugin structure
* complete converting base test classes
* add options to support TLS cetificate verification
* add object-store show commands for container and object

0.2.2 (20 Sep 2013)
===================

* add object-store list commands and API library
* add test structure

0.2.1 (06 Aug 2013)
===================

* sync requirements.txt, test-requirements.txt
* remove d2to1 dependency

0.2.0 (02 Aug 2013)
===================

* Initial public release to PyPI
* Implemented Compute, Identity, Image and Volume API commands
