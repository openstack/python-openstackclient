===============================
Developing with OpenStackClient
===============================

Communication
-------------

Meetings
=========
The OpenStackClient team meets regularly on every Thursday.  For details
please refer to the `wiki`_.

.. _`wiki`: https://wiki.openstack.org/wiki/Meetings/OpenStackClient

Testing
-------

Using ``tox``
=============

Before running tests, you should have ``tox`` installed and available in your
environment:

.. code-block:: bash

    $ pip install tox

To execute the full suite of tests maintained within OpenStackClient, run:

.. code-block:: bash

    $ tox

.. NOTE::

    The first time you run ``tox``, it will take additional time to build
    virtualenvs. You can later use the ``-r`` option with ``tox`` to rebuild
    your virtualenv in a similar manner.

To run tests for one or more specific test environments (for example, the most
common configuration of Python 2.7 and PEP-8), list the environments with the
``-e`` option, separated by spaces:

.. code-block:: bash

    $ tox -e py27,pep8

See ``tox.ini`` for the full list of available test environments.

Running functional tests
========================

OpenStackClient also maintains a set of functional tests that are optimally
designed to be run against OpenStack's gate. Optionally, a developer may
choose to run these tests against any OpenStack deployment, however depending
on the services available, results will vary.

To run the entire suite of functional tests:

.. code-block:: bash

    $ tox -e functional

To run a specific functional test:

.. code-block:: bash

    $ tox -e functional -- --regex functional.tests.compute.v2.test_server

Running with PDB
================

Using PDB breakpoints with ``tox`` and ``testr`` normally doesn't work since
the tests fail with a `BdbQuit` exception rather than stopping at the
breakpoint.

To run with PDB breakpoints during testing, use the `debug` ``tox`` environment
rather than ``py27``. Here's an example, passing the name of a test since
you'll normally only want to run the test that hits your breakpoint:

.. code-block:: bash

    $ tox -e debug opentackclient.tests.identity.v3.test_group

For reference, the `debug` ``tox`` environment implements the instructions
here: https://wiki.openstack.org/wiki/Testr#Debugging_.28pdb.29_Tests


Building the Documentation
--------------------------

The documentation is generated with Sphinx using the ``tox`` command. To
create HTML docs, run the following:

.. code-block:: bash

    $ tox -e docs

The resultant HTML will be the ``doc/build/html`` directory.

Release Notes
-------------

The release notes for a patch should be included in the patch.  See the
`Project Team Guide`_ for more information on using reno in OpenStack.

.. _`Project Team Guide`: http://docs.openstack.org/project-team-guide/release-management.html#managing-release-notes

If any of the following applies to the patch, a release note is required:

* The deployer needs to take an action when upgrading
* The plugin interface changes
* A new feature is implemented
* A command or option is removed
* Current behavior is changed
* A security bug is fixed

Reno is used to generate release notes. Please read the docs for details. In summary, use

.. code-block:: bash

    $ tox -e venv -- reno new <bug-,bp-,whatever>

Then edit the sample file that was created and push it with your change.

To see the results:

.. code-block:: bash

    $ git commit  # Commit the change because reno scans git log.

    $ tox -e releasenotes

Then look at the generated release notes files in releasenotes/build/html in your favorite browser.

Testing new code
----------------

If a developer wants to test new code (feature, command or option) that
they have written, OpenStackClient may be installed from source by running
the following commands in the base directory of the project:

.. code-block:: bash

   $ python setup.py develop

or

.. code-block:: bash

   $ pip install -e .
