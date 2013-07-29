OpenStack Style Commandments
============================

Step 0: Read https://github.com/openstack-dev/hacking/blob/master/HACKING.rst
Step 1: Read http://www.python.org/dev/peps/pep-0008/ one more time
Step 2: Read on

General
-------
- thou shalt not violate causality in our time cone, or else

Docstrings
----------

Docstrings should ONLY use triple-double-quotes (``"""``)

Single-line docstrings should NEVER have extraneous whitespace
between enclosing triple-double-quotes.

Deviation! Sentence fragments do not have punctuation.  Specifically in the
command classes the one line docstring is also the help string for that
command and those do not have periods.

  """A one line docstring looks like this"""

Calling Methods
---------------

Deviation! When breaking up method calls due to the 79 char line length limit,
use the alternate 4 space indent.  With the frist argument on the succeeding
line all arguments will then be vertically aligned.  Use the same convention
used with other data structure literals and terminate the method call with
the last argument line ending with a comma and the closing paren on its own
line indented to the starting line level.

    unnecessarily_long_function_name(
        'string one',
        'string two',
        kwarg1=constants.ACTIVE,
        kwarg2=['a', 'b', 'c'],
    )

Text encoding
-------------

Note: this section clearly has not been implemented in this project yet, it is
the intention to do so.

All text within python code should be of type 'unicode'.

    WRONG:

    >>> s = 'foo'
    >>> s
    'foo'
    >>> type(s)
    <type 'str'>

    RIGHT:

    >>> u = u'foo'
    >>> u
    u'foo'
    >>> type(u)
    <type 'unicode'>

Transitions between internal unicode and external strings should always
be immediately and explicitly encoded or decoded.

All external text that is not explicitly encoded (database storage,
commandline arguments, etc.) should be presumed to be encoded as utf-8.

    WRONG:

    mystring = infile.readline()
    myreturnstring = do_some_magic_with(mystring)
    outfile.write(myreturnstring)

    RIGHT:

    mystring = infile.readline()
    mytext = s.decode('utf-8')
    returntext = do_some_magic_with(mytext)
    returnstring = returntext.encode('utf-8')
    outfile.write(returnstring)

Python 3.x Compatibility
------------------------

OpenStackClient strives to be Python 3.3 compatibile.  Common guidelines:

* Convert print statements to functions: print statements should be converted
  to an appropriate log or other output mechanism.
* Use six where applicable: x.iteritems is converted to six.iteritems(x)
  for example.

Running Tests
-------------

Note: Oh boy, are we behing on writing tests.  But they are coming!

The testing system is based on a combination of tox and testr. If you just
want to run the whole suite, run `tox` and all will be fine. However, if
you'd like to dig in a bit more, you might want to learn some things about
testr itself. A basic walkthrough for OpenStack can be found at
http://wiki.openstack.org/testr
