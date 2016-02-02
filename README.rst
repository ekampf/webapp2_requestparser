===============================
WebApp2 RequestParser
===============================

.. image:: https://travis-ci.org/ekampf/webapp2_restful.svg
        :target: https://travis-ci.org/ekampf/webapp2_restful

.. image:: https://coveralls.io/repos/ekampf/webapp2_restful/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/ekampf/webapp2_restful?branch=master

.. image:: https://img.shields.io/pypi/v/webapp2_restful.svg
        :target: https://pypi.python.org/pypi/webapp2_restful


The *webapp2_restful* library is a Request parsing interface inspired by `restful-flask's request parser  <http://flask-restful.readthedocs.org/en/latest/reqparse.html>`_.

Its interface is modelled after the `argparse <http://docs.python.org/dev/library/argparse.html>`_ interface.

Its goal is to provide a uniform access to any variable on the webapp2.Request object and allowing handlers to provide a sort of "contract" where they
specify the parameters they expect to be called with - making code easier to read and understand.

* Free software: BSD license
* Documentation: https://webapp2_restful.readthedocs.org.
<TBD - Documentation is still partial but mostly follows the same API the Flask library provide with a few additions>

**********************
Basic Argument Parsing
**********************

Here’s a simple example of the request parser.
It looks for two arguments in the webapp2.Request's *json* and *params* properties: one of type int, and the other of type str::

  from webapp2_restful.parser import RequestParser

  parser = RequestParser()
  parser.add_argument('rate', type=int, help='Rate cannot be converted')
  parser.add_argument('name', type=str)
  args = parser.parse_args(self.request)


**********************************
Special Google AppEngine Arguments
**********************************

::

  from webapp2_restful.parser import RequestParser
  from webapp2_restful.arguments_ndb import EntityIDArgument

  parser = RequestParser()
  parser.add_argument('store_id', type=EntityIDArgument(Store), dest='store')
  args = parser.parse_args(self.request)

  # args.store is a Store instance
  print(args.store)

