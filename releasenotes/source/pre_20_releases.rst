================
Pre-2.0 Releases
================

1.9.0 (17 Nov 2015)
===================

* Several updates to `openstack server`
  Blueprint :oscbp:`servers <cmd-with-multi-servers>`

  * `openstack server start`
  * `openstack server stop`
  * `openstack server pause`
  * `openstack server unpause`
  * `openstack server lock`
  * `openstack server unlock`

* Obfuscate passwords when used in debug mode
  Bug `1501598 <https://bugs.launchpad.net/bugs/1501598>`_

* Clean up `identity provider show`
  Bug `1478995 <https://bugs.launchpad.net/bugs/1478995>`_

* Add `description` to `identity provider set`
  Bug `1515815 <https://bugs.launchpad.net/bugs/1515815>`_

* Add `compute service delete`
  Bug `1503510 <https://bugs.launchpad.net/bugs/1503510>`_

* Log a warning when setting non-ascii object store properties
  Bug `1503898 <https://bugs.launchpad.net/bugs/1503898>`_

* Add 'marker' and 'limit' to `openstack flavor list`
  Bug `1505874 <https://bugs.launchpad.net/bugs/1505874>`_

* Remove `url` from `region create` and `region set`
  Bug `1506841 <https://bugs.launchpad.net/bugs/1506841>`_

* `openstack image add project` fails with AttributeError for image v2
  Bug `1509054 <https://bugs.launchpad.net/bugs/1509054>`_

* Inconsistent output with `openstack usage show`
  Bug `1512220 <https://bugs.launchpad.net/bugs/1512220>`_

* Validate --lines with `openstack console log show`
  Bug `1512263 <https://bugs.launchpad.net/bugs/1512263>`_

* Validate --project does not exist with `openstack quota set`
  Bug `1512638 <https://bugs.launchpad.net/bugs/1512638>`_

* Cannot list servers while --user specified for `openstack server list`
  Bug `1513701 <https://bugs.launchpad.net/bugs/1513701>`_

* Cannot list volumes while --user specified for `openstack volume list`
  Bug `1514145 <https://bugs.launchpad.net/bugs/1514145>`_

* Cannot find volume with --block-device-mapping with `openstack server create`
  Bug `1514394 <https://bugs.launchpad.net/bugs/1514394>`_

* Fix documentation for `credential set`
  Bug `1418837 <https://bugs.launchpad.net/bugs/1418837>`_

1.8.0 (18 Oct 2015)
===================

* `image create --volume` command (v1) will attempt to create two images
  Bug `1497221 <https://bugs.launchpad.net/bugs/1497221>`_

* Add filtering by project/uesr for command `volume list`
  Bug `1483976 <https://bugs.launchpad.net/bugs/1483976>`_

* Password used by plugin shows up in debug mode
  Bug `1501598 <https://bugs.launchpad.net/bugs/1501598>`_

* Add support for `object store account`
  Bug `1501943 <https://bugs.launchpad.net/bugs/1501943>`_

* Add support for setting properties on objects and containers
  Bug `1501945 <https://bugs.launchpad.net/bugs/1501945>`_

* `role list` ignores `--inherited` option
  Bug `1502822 <https://bugs.launchpad.net/bugs/1502822>`_

* `compute service list` does not return service ID number
  Bug `1503430 <https://bugs.launchpad.net/bugs/1503430>`_

* Containers and objects with non-ascii characters fails
  Bug `1503508 <https://bugs.launchpad.net/bugs/1503508>`_

1.7.1 (30 Sep 2015)
===================

* Image v2 lookup issues
  Bug `1501362 <https://bugs.launchpad.net/bugs/1501362>`_

1.7.0 (22 Sep 2015)
===================

* Add support for v2 image create/update commands
  Bug `1405562 <https://bugs.launchpad.net/bugs/1405562>`_

* ICMP secgroup rule must have ``--dst-port -1`` to actually allow ICMP
  Bug `1477629 <https://bugs.launchpad.net/bugs/1477629>`_

* Add a blurb about ``pip install -e .`` to the developer docs
  Bug `1483384 <https://bugs.launchpad.net/bugs/1483384>`_

* Add filtering by user for command 'openstack server list'
  Bug `1483974 <https://bugs.launchpad.net/bugs/1483974>`_

* No support for listing servers of other project with openstack server list
  Bug `1488486 <https://bugs.launchpad.net/bugs/1488486>`_

* Missing image causes confusing 'server show' response
  Bug `1489901 <https://bugs.launchpad.net/bugs/1489901>`_

* Volume Attached to is incorrect
  Bug `1489954 <https://bugs.launchpad.net/bugs/1489954>`_

* novaclient 2.27.0 breaks version handling
  Bug `1492467 <https://bugs.launchpad.net/bugs/1492467>`_

* Support listing users in a non-default domain scoped group
  Bug `1492916 <https://bugs.launchpad.net/bugs/1492916>`_

* ERROR: InvocationError:
  '/opt/stack/new/python-openstackclient/.tox/functional/bin/ostestr'
  in gate-osc-dsvm-functional
  Bug `1496337 <https://bugs.launchpad.net/bugs/1496337>`_

* image list --long is broken with v2
  Bug `1498150 <https://bugs.launchpad.net/bugs/1498150>`_

* Add ``--log-file`` option support

* Set default Block Storage API version to ``2``

1.6.0 (10 Aug 2015)
===================

* Added support for Block Storage v2 APIs
  Blueprint `volume-v2 <https://blueprints.launchpad.net/python-openstackclient/+spec/volume-v2>`_

  * Backup
  * Snapshot
  * Volume
  * Volume Type
  * Volume QoS

* Updated ``python-cliff`` provides improved UX

  * -h and --help revert to top level help when used in a subcommand
    Bug `1444983 <https://bugs.launchpad.net/bugs/1444983>`_

  * suggest commands if command is not recognized
    Bug `1462192 <https://bugs.launchpad.net/bugs/1462192>`_

* Bad argument passed to inherited role assignments CRUD
  Bug `1482254 <https://bugs.launchpad.net/bugs/1482254>`_

* quota show for a project blows up
  Bug `1481803 <https://bugs.launchpad.net/bugs/1481803>`_

* Unscoped saml auth error message refers to invalid option os-auth-type
  Bug `1477083 <https://bugs.launchpad.net/bugs/1477083>`_

* Need a command to show current configuration
  Bug `1476729 <https://bugs.launchpad.net/bugs/1476729>`_

* type should be volume_type
  Bug `1475958 <https://bugs.launchpad.net/bugs/1475958>`_

* openstack volume(v1) type missing show
  Bug `1475879 <https://bugs.launchpad.net/bugs/1475879>`_

* property should be required argument in unset cmd
  Bug `1475872 <https://bugs.launchpad.net/bugs/1475872>`_

* --or-show missing from some command docs
  Bug `1475485 <https://bugs.launchpad.net/bugs/1475485>`_

* missing project-domain to prevent project name collisions for user v3
  Bug `1475357 <https://bugs.launchpad.net/bugs/1475357>`_

* Cannot manipulate group member by ID
  Bug `1475127 <https://bugs.launchpad.net/bugs/1475127>`_

* glance client expects image ID only, should use base resource
  Bug `1475001 <https://bugs.launchpad.net/bugs/1475001>`_

* trust roles display a trailing character upon show and create
  Bug `1474707 <https://bugs.launchpad.net/bugs/1474707>`_

* catalog list fails in identity v2
  Bug `1474656 <https://bugs.launchpad.net/bugs/1474656>`_

* openstack flavor unset NoneType error when used without --proprty
  Bug `1474237 <https://bugs.launchpad.net/bugs/1474237>`_

* TypeError: 'NoneType' object does not support item assignment with latest os-client-config
  Bug `1473921 <https://bugs.launchpad.net/bugs/1473921>`_

* authentication fails when openstackclient prompts for a password
  Bug `1473862 <https://bugs.launchpad.net/bugs/1473862>`_

* New mock release(1.1.0) broke unit/function tests
  Bug `1473454 <https://bugs.launchpad.net/bugs/1473454>`_

* Cannot create keystone trust with python-openstackclient using trustor/trustee id
  Bug `1473298 <https://bugs.launchpad.net/bugs/1473298>`_

* "role assignment list" fails if two users in different domains have the same name
  Bug `1472909 <https://bugs.launchpad.net/bugs/1472909>`_

* openstack catalog list always returns publicURL
  Bug `1472629 <https://bugs.launchpad.net/bugs/1472629>`_

* The network list --dhcp option is inconsistent
  Bug `1472613 <https://bugs.launchpad.net/bugs/1472613>`_

* Add support for showing aggregates in an hypervisor's properties
  Bug `1470875 <https://bugs.launchpad.net/bugs/1470875>`_

* Can't seem to be able to get Openstackclient/examples to work
  Bug `1470272 <https://bugs.launchpad.net/bugs/1470272>`_

* openstack server ssh fails to see floating IP address
  Bug `1469843 <https://bugs.launchpad.net/bugs/1469843>`_

* confused domain argument for network create v2
  Bug `1468988 <https://bugs.launchpad.net/bugs/1468988>`_

* small typo in network.rst
  Bug `1468282 <https://bugs.launchpad.net/bugs/1468282>`_

* Add support for Cinder volume qos commands
  Bug `1467967 <https://bugs.launchpad.net/bugs/1467967>`_

* mismatch option in server.rst
  Bug `1466742 <https://bugs.launchpad.net/bugs/1466742>`_

* user create mismatch object name in doc
  Bug `1466738 <https://bugs.launchpad.net/bugs/1466738>`_

* Existing image is updated when call image create
  Bug `1461817 <https://bugs.launchpad.net/bugs/1461817>`_

* ERROR: openstack 'ArgumentParser' object has no attribute 'debug'
  Bug `1459519 <https://bugs.launchpad.net/bugs/1459519>`_

* Add an --os-endpoint-type cli optional argument to be able to select endpoint interface type
  Bug `1454392 <https://bugs.launchpad.net/bugs/1454392>`_

* API versions are ignored from OCC
  Bug `1453229 <https://bugs.launchpad.net/bugs/1453229>`_

* Issues with OpenStackClient / Locale / OSX
  Bug `1436898 <https://bugs.launchpad.net/bugs/1436898>`_

* Image sharing does not seem to be supported
  Bug `1402420 <https://bugs.launchpad.net/bugs/1402420>`_

* rename requires files to standard names
  Bug `1179008 <https://bugs.launchpad.net/bugs/1179008>`_

1.5.0 (16 Jun 2015)
===================

* openstack 'ListEC2Creds' object has no attribute 'determine_ec2_user'
  Bug `1465561 <https://bugs.launchpad.net/bugs/1465561>`_

1.4.0 (11 Jun 2015)
===================

* AttributeError: 'Client' object has no attribute 'ec2'
  Bug `1236326 <https://bugs.launchpad.net/bugs/1236326>`_

* Group/role identity v3 commands have no option for domain to operate on
  Bug `1446546 <https://bugs.launchpad.net/bugs/1446546>`_

* ``--insecure`` is ignored if ``OS_CACERT`` env var is set
  Bug `1447784 <https://bugs.launchpad.net/bugs/1447784>`_

* ``security group list`` always uses identity admin endpoint
  Bug `1459629 <https://bugs.launchpad.net/bugs/1459629>`_

* Race failure to delete security group
  Bug `1460112 <https://bugs.launchpad.net/bugs/1460112>`_

* v3 project set is missing ``--domain`` argument
  Bug `1460122 <https://bugs.launchpad.net/bugs/1460122>`_

* Project create is missing ``--parent`` argument in doc
  Bug `1460256 <https://bugs.launchpad.net/bugs/1460256>`_

* v3 ``role add`` is missing domain scope arguments in doc
  Bug `1460296 <https://bugs.launchpad.net/bugs/1460296>`_

* Cannot force v2password auth plugin
  Bug `1460369 <https://bugs.launchpad.net/bugs/1460369>`_

* Let's not use the deprecated argument
  Bug `1462389 <https://bugs.launchpad.net/bugs/1462389>`_

1.3.0 (27 May 2015)
===================

* Need to specify domain with role list
  Bug `1421328 <https://bugs.launchpad.net/bugs/1421328>`_

* Add support for keystone service providers
  Bug `1435962 <https://bugs.launchpad.net/bugs/1435962>`_

* Can't update disk_format and container_format of image
  Bug `1446362 <https://bugs.launchpad.net/bugs/1446362>`_

* Openstack --os-image-api-version 2 image show <image_id> fails
  Bug `1450829 <https://bugs.launchpad.net/bugs/1450829>`_

* The insecure option is ignored for command line options and OCC
  Bug `1450855 <https://bugs.launchpad.net/bugs/1450855>`_

* Delete security group rule broken
  Bug `1450872 <https://bugs.launchpad.net/bugs/1450872>`_

* Quota set sends invalid messages
  Bug `1451640 <https://bugs.launchpad.net/bugs/1451640>`_

* Keystone Access Log logs "python-keystoneclient" as User-Agent even when request is made by openstack client
  Bug `1453995 <https://bugs.launchpad.net/bugs/1453995>`_

* Client error while rescuing an instance
  Bug `1457983 <https://bugs.launchpad.net/bugs/1457983>`_


1.2.0 (30 Apr 2015)
===================

* Fix error in ``security group create`` command when ``--description`` is not
  supplied.
  Bug `1434172 <https://bugs.launchpad.net/bugs/1434172>`_

* Correct ``image list`` pagination handling, all images are now correctly returned.
  Bug `1443089 <https://bugs.launchpad.net/bugs/1443089>`_

* Do not require ``--dst-port`` option with ``security group rule create`` when
  ``--proto ICMP`` is selected.
  Bug `1443963 <https://bugs.launchpad.net/bugs/1443963>`_

* Correctly pass ``--location`` arguemnt in ``image create`` command.
  Bug `1445460 <https://bugs.launchpad.net/bugs/1445460>`_

* Correctly handle use of ``role`` commands for project admins.  Using IDs will
  work for project admins even when names will not due to non-admin contraints.
  Bug `1445528 <https://bugs.launchpad.net/bugs/1445528>`_

* Correctly exit with an error when authentication can not be completed.
  Bug `1444640 <https://bugs.launchpad.net/bugs/1444640>`_

* Fix ``backup create`` to correctly use the ``--container`` value if supplied.
  Bug `1446751 <https://bugs.launchpad.net/bugs/1446751>`_

* Document the backward-compatibility-breaking changes in
  :oscdoc:`Backwards Incompatible Changes <backwards-incompatible>`.
  :lpbug:`1406470`

* Add ``--parent`` option to ``project create`` command


1.1.0 (21 Apr 2015)
===================

* Add global ``--os-cloud`` option to select from a list of cloud configurations.
  See :oscdoc:`Configuration <configuration>` for more details.

* Fix global ``--timing`` option operation.
  Bug `1402577 <https://bugs.launchpad.net/bugs/1402577>`_

* Add ``flavor set`` and ``flavor unset`` commands.
  Bug `1434137 <https://bugs.launchpad.net/bugs/1434137>`_

* Add ``--domain`` and ``--project`` options to ``network create`` command.
  Bug `1435640 <https://bugs.launchpad.net/bugs/1435640>`_

* Add ``--volume-type`` option to ``quota set`` command.
  Bug `1438377 <https://bugs.launchpad.net/bugs/1438377>`_

* Add ``--domain`` and ``--project`` options to ``limits show`` command.
  Bug `1438379 <https://bugs.launchpad.net/bugs/1438379>`_

* Improve ``--nic`` option help for ``server create`` command.
  Bug `1444685 <https://bugs.launchpad.net/bugs/1444685>`_

* Add ``--remote-id`` and ``--remote-id-file`` options to
  ``identity provider create`` and ``identity provider set`` commands.


1.0.3 (10 Mar 2015)
===================

* Add ``catalog list`` and ``catalog show`` commands for Identity v3.

* Add 'hypervisor stats show' command .
  Bug `1423748 <https://bugs.launchpad.net/bugs/1423748>`_

* Rename ``server resize`` option ``--verify`` to ``confirm``.  It conflicted with
  the global ``--verify`` option and never worked prior to this.
  Bug `1416542 <https://bugs.launchpad.net/bugs/1416542>`_

* Add ``trust create/delete/list/show`` commands.
  Bug `1413718 <https://bugs.launchpad.net/bugs/1413718>`_

* Add ``--sort`` to ``image list`` command.
  Bug `1410251 <https://bugs.launchpad.net/bugs/1410251>`_

* Change ``volume create`` option ``--snapshot-id`` to ``--snapshot``.  The old
  name is still silently supported.
  Bug `1418742 <https://bugs.launchpad.net/bugs/1418742>`_

* Add Network API quotas to ``quota show`` command.
  Bug `1411160 <https://bugs.launchpad.net/bugs/1411160>`_

* Add ``--public``, ``--private``, ``--all``, ``--long`` options to
  ``flavor list`` command.  Remove "Extra Specs", "Swap" and"RXTX Factor"
  columns from default output.
  Bug `1411160 <https://bugs.launchpad.net/bugs/1411160>`_:

* Add ``--shared``, ``--property`` options to ``image list`` command.
  Bug `1401902 <https://bugs.launchpad.net/bugs/1401902>`_

* Add ``--size`` option to ``volume set`` command.
  Bug `1413954 <https://bugs.launchpad.net/bugs/1413954>`_

* Bug `1353040 <https://bugs.launchpad.net/bugs/1353040>`_: server create --nic option clumsy
* Bug `1366279 <https://bugs.launchpad.net/bugs/1366279>`_: nova lock command description rather terse
* Bug `1399588 <https://bugs.launchpad.net/bugs/1399588>`_: Authentication needed for help command
* Bug `1401902 <https://bugs.launchpad.net/bugs/1401902>`_: image filtering not available
* Bug `1410251 <https://bugs.launchpad.net/bugs/1410251>`_: sort and filter options on openstack image list
* Bug `1411160 <https://bugs.launchpad.net/bugs/1411160>`_: Add network support to quota show
* Bug `1413718 <https://bugs.launchpad.net/bugs/1413718>`_: support keystone v3 trust extension
* Bug `1413954 <https://bugs.launchpad.net/bugs/1413954>`_: missing volume extend
* Bug `1415182 <https://bugs.launchpad.net/bugs/1415182>`_: Add extra validation when extending volume
* Bug `1416542 <https://bugs.launchpad.net/bugs/1416542>`_: openstack client resize verify not completing workflow
* Bug `1416780 <https://bugs.launchpad.net/bugs/1416780>`_: flavor list missing features
* Bug `1417614 <https://bugs.launchpad.net/bugs/1417614>`_: tenant_id in server show
* Bug `1417854 <https://bugs.launchpad.net/bugs/1417854>`_: Fix help messages for `os security group rule create` and `os security group rule list`
* Bug `1418024 <https://bugs.launchpad.net/bugs/1418024>`_: wrong import of contrib module from novaclient
* Bug `1418384 <https://bugs.launchpad.net/bugs/1418384>`_: openstack client help shows domain can be changed for a project
* Bug `1418742 <https://bugs.launchpad.net/bugs/1418742>`_: volume create --snapshot-id is wrong
* Bug `1418810 <https://bugs.launchpad.net/bugs/1418810>`_: auth with os-token fails with unexpected keyword argument 'user_domain_id'
* Bug `1420080 <https://bugs.launchpad.net/bugs/1420080>`_: functional tests are failing with new keystoneclient release
* Bug `1420732 <https://bugs.launchpad.net/bugs/1420732>`_: Better error message for sort_items
* Bug `1423748 <https://bugs.launchpad.net/bugs/1423748>`_: Add support for hypervisor-stats and hypervisor-uptime command
* Bug `1428912 <https://bugs.launchpad.net/bugs/1428912>`_: authentication through password prompting is broken
* Bug `1429211 <https://bugs.launchpad.net/bugs/1429211>`_: 'catalog list' fails when region is not present


1.0.2 (19 Jan 2015)
===================

* The OpenStackClient content from the OpenStack Wiki has been migrated into
  the OSC source repo.  This includes the :oscdoc:`Command Structure <commands>`,
  :oscdoc:`Command List <command-list>` and
  :oscdoc:`Human Interface Guide <humaninterfaceguide>` documents.

* Set a default domain ID when both ``OS_USER_DOMAIN_ID`` and
  ``OS_USER_DOMAIN_NAME`` are not set.  This is also done for
  ``OS_PROJECT_DOMAIN_ID`` and ``OS_PROJECT_DOMAIN_NAME``.
  (*Identity API v3 only*).
  Bug `1385338 <https://bugs.launchpad.net/bugs/1385338>`_: Improve domain related defaults when using v3 identity

* Add new ``usage show`` command to display project resource usage information.
  Bug `1400796 <https://bugs.launchpad.net/bugs/1400796>`_: Quick usage report - nova usage

* Add ``--project`` option to ``user list`` command to filter users by project
  (*Identity API v3 only*).
  Bug `1397251 <https://bugs.launchpad.net/bugs/1397251>`_: allow `openstack user list` to use other filters

* Add ``--user`` to ``project list`` command to filter projects by user
  (*Identity API v3 only*).
  Bug `1394793 <https://bugs.launchpad.net/bugs/1394793>`_: support the keystone api /v3/users/$userid/projects

* Add ``--project`` and ``--user`` options to ``role list`` to filter roles
  by project and/or user.  This makes the v2 command very similar to the
  v3 command.
  (*Identity API v2 only*).
  Bug `1406737 <https://bugs.launchpad.net/bugs/1406737>`_: `user role list` command should be worked into `role list`

* Bug `1385338 <https://bugs.launchpad.net/bugs/1385338>`_: Improve domain related defaults when using v3 identity API
* Bug `1390507 <https://bugs.launchpad.net/bugs/1390507>`_: Quota show requires cinder in keystone catalog
* Bug `1394793 <https://bugs.launchpad.net/bugs/1394793>`_: support the keystone api /v3/users/$userid/projects
* Bug `1397251 <https://bugs.launchpad.net/bugs/1397251>`_: allow `openstack user list` to use other filters
* Bug `1399757 <https://bugs.launchpad.net/bugs/1399757>`_: ec2 credentials create fails in 1.0.0
* Bug `1400531 <https://bugs.launchpad.net/bugs/1400531>`_: Authentication failure results in useless error message
* Bug `1400597 <https://bugs.launchpad.net/bugs/1400597>`_: delete multiple objects
* Bug `1400795 <https://bugs.launchpad.net/bugs/1400795>`_: No list availability zones option
* Bug `1400796 <https://bugs.launchpad.net/bugs/1400796>`_: Quick usage report - nova usage
* Bug `1404073 <https://bugs.launchpad.net/bugs/1404073>`_: type should be required for v2.0 service create
* Bug `1404434 <https://bugs.launchpad.net/bugs/1404434>`_: add missing docs for service command
* Bug `1404931 <https://bugs.launchpad.net/bugs/1404931>`_: volume list does not show attached servers
* Bug `1404997 <https://bugs.launchpad.net/bugs/1404997>`_: Allow description to be set for service create/update
* Bug `1405416 <https://bugs.launchpad.net/bugs/1405416>`_: Compute region selection broken
* Bug `1406654 <https://bugs.launchpad.net/bugs/1406654>`_: Remove deprecated commands from help
* Bug `1406737 <https://bugs.launchpad.net/bugs/1406737>`_: v3 endpoint related commands access service.name without check
* Bug `1408585 <https://bugs.launchpad.net/bugs/1408585>`_: Backup list doesn't show backup's name
* Bug `1409179 <https://bugs.launchpad.net/bugs/1409179>`_: `user role list` command should be worked into `role list`
* Bug `1410364 <https://bugs.launchpad.net/bugs/1410364>`_: Version discovery fails with default Keystone config
* Bug `1411179 <https://bugs.launchpad.net/bugs/1411179>`_: network client don't use session
* Bug `1411337 <https://bugs.launchpad.net/bugs/1411337>`_: identity v3 service list should have "description" column


1.0.1 (08 Dec 2014)
===================

* Bug `1399757 <https://bugs.launchpad.net/bugs/1399757>`_: EC2 credentials create fails


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
