===============================
Developing with OpenStackClient
===============================

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
