*******************
HTSQL_SPSS Overview
*******************

The ``htsql_spss`` package is an extension for `HTSQL`_ that adds basic
support for the IBM SPSS file format.

.. _`HTSQL`: http://htsql.org/


Installation
============

Install this package like you would any other Python package::

    $ pip install htsql_spss

Then, enable the ``htsql_spss`` extension when you invoke HTSQL. E.g.::

    $ htsql-ctl -E htsql_spss ...

Or, in your HTSQL configuration YAML file::

    htsql:
      db: ...
    htsql_spss:


Formatters
==========

This extension adds a formatter function to HTSQL: ``/:spss``.
This is a tabular formatter (like ``/:csv``)
that will output the results in in IBM SPSS format.


License/Copyright
=================

This project is released under the Apache v2 license. See the accompanying
``LICENSE.rst`` file for details.

Copyright (c) 2016, Prometheus Research, LLC

