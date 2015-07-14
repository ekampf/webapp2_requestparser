# -*- coding: utf-8 -*-
__author__ = 'ekampf'

import unittest
from mock import Mock, NonCallableMock
from webapp2 import Request

from webapp2_requestparser.parser import Argument, Namespace, RequestParser, InvalidParameterValue


class TestRequestParserArgument(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # region Namespace tests
    def test_namespace_existence(self):
        namespace = Namespace()
        namespace.foo = 'bar'
        namespace['bar'] = 'baz'
        self.assertEqual(namespace['foo'], 'bar')
        self.assertEqual(namespace.bar, 'baz')

    def test_namespace_missing(self):
        namespace = Namespace()
        self.assertRaises(AttributeError, lambda: namespace.spam)
        self.assertRaises(KeyError, lambda: namespace['eggs'])

    def test_namespace_configurability(self):
        self.assertTrue(isinstance(RequestParser().parse_args(None), Namespace))
        self.assertTrue(type(RequestParser(namespace_class=dict).parse_args(None)) is dict)
    # endregion

    # region Argument params
    def test_name(self):
        arg = Argument("foo")
        self.assertEqual(arg.name, "foo")

    def test_dest(self):
        arg = Argument("foo", dest="foobar")
        self.assertEqual(arg.dest, "foobar")

    def test_default_help(self):
        arg = Argument("foo")
        self.assertEqual(arg.help, None)

    def test_type(self):
        arg = Argument("foo", type=int)
        self.assertEqual(arg.type, int)

    def test_default(self):
        arg = Argument("foo", default=True)
        self.assertEqual(arg.default, True)

    def test_required(self):
        arg = Argument("foo", required=True)
        self.assertEqual(arg.required, True)

    def test_ignore(self):
        arg = Argument("foo", ignore=True)
        self.assertEqual(arg.ignore, True)

    def test_action_filter(self):
        arg = Argument("foo", action="filter")
        self.assertEqual(arg.action, u"filter")

    def test_action(self):
        arg = Argument("foo", action="append")
        self.assertEqual(arg.action, u"append")

    def test_choices(self):
        arg = Argument("foo", choices=[1, 2])
        self.assertEqual(arg.choices, [1, 2])

    def test_default_dest(self):
        arg = Argument("foo")
        self.assertEqual(arg.dest, None)

    def test_default_default(self):
        arg = Argument("foo")
        self.assertEqual(arg.default, None)

    def test_required_default(self):
        arg = Argument("foo")
        self.assertEqual(arg.required, False)

    def test_ignore_default(self):
        arg = Argument("foo")
        self.assertEqual(arg.ignore, False)

    def test_action_default(self):
        arg = Argument("foo")
        self.assertEqual(arg.action, u"store")

    def test_choices_default(self):
        arg = Argument("foo")
        self.assertEqual(len(arg.choices), 0)

    def test_source(self):
        req = Mock(['args', 'headers', 'values'])
        req.args = {'foo': 'bar'}
        req.headers = {'baz': 'bat'}
        arg = Argument('foo', location=['args'])
        self.assertEqual(arg.source(req), req.args)

        arg = Argument('foo', location=['headers'])
        self.assertEqual(arg.source(req), req.headers)

    def test_source_bad_location(self):
        req = Mock(['params'])
        arg = Argument('foo', location=['foo'])
        self.assertTrue(len(arg.source(req)) == 0) # yes, basically you don't find it

    def test_source_default_location(self):
        req = Mock(['params'])
        req._get_child_mock = lambda **kwargs: NonCallableMock(**kwargs)
        arg = Argument('foo')
        self.assertEqual(arg.source(req), req.params)

    def test_option_case_sensitive(self):
        arg = Argument("foo", choices=["bar", "baz"], case_sensitive=True)
        self.assertEqual(True, arg.case_sensitive)

        # Insensitive
        arg = Argument("foo", choices=["bar", "baz"], case_sensitive=False)
        self.assertEqual(False, arg.case_sensitive)

        # Default
        arg = Argument("foo", choices=["bar", "baz"])
        self.assertEqual(True, arg.case_sensitive)


    # endregion

    # region Request Parser

    def testRequestParser_json_body(self):
        req = Request.blank('/', POST='{ "foo": "bar" }', environ={
            'CONTENT_TYPE': 'application/json;"',
        })
        parser = RequestParser()
        parser.add_argument("foo", type=lambda x: x*2, required=False)

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], "barbar")

    def testRequestParser_type_is_callable(self):
        req = Request.blank("/bubble?foo=1")

        parser = RequestParser()
        parser.add_argument("foo", type=lambda x: x*2, required=False)

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], "11")

    def testRequestParser_noParams_returnsNone(self):
        req = Request.blank('/')

        parser = RequestParser()
        parser.add_argument("foo")

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], None)

    def testRequestParser_noParamsWithDefault_returnsDefault(self):
        req = Request.blank('/')

        parser = RequestParser()
        parser.add_argument('foo', default='faa')

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], 'faa')

    def testRequestParser_choices_correctValue(self):
        req = Request.blank('/stam?foo=bar')

        parser = RequestParser()
        parser.add_argument("foo", choices=["bar"])

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], 'bar')

    def testRequestParser_choices_incorrectValue(self):
        req = Request.blank('/stam?foo=bat')

        parser = RequestParser()
        parser.add_argument("foo", choices=["bar"])

        self.assertRaises(InvalidParameterValue, lambda: parser.parse_args(req))

    # endregion

