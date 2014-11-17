=============
Release Notes
=============

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
