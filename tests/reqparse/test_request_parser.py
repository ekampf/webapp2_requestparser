# -*- coding: utf-8 -*-
import json
import unittest
from mock import Mock, NonCallableMock
from webapp2 import Request

from webapp2_restful.reqparse import Argument, Namespace, RequestParser, InvalidParameterValue, MissingParameterError

__author__ = 'ekampf'


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

    def test_default(self):
        arg = Argument("foo", default=True)
        self.assertEquals(arg.default, True)

    def test_dest(self):
        arg = Argument("foo", dest="foobar")
        self.assertEqual(arg.dest, "foobar")

    def test_default_help(self):
        arg = Argument("foo")
        self.assertEqual(arg.help, None)

    def test_location_url(self):
        arg = Argument("foo", location="url")
        self.assertEquals(arg.location, "url")

    def test_location_url_list(self):
        arg = Argument("foo", location=["url"])
        self.assertEquals(arg.location, ["url"])

    def test_location_header(self):
        arg = Argument("foo", location="headers")
        self.assertEquals(arg.location, "headers")

    def test_location_json(self):
        arg = Argument("foo", location="json")
        self.assertEquals(arg.location, "json")

    def test_location_get_json(self):
        arg = Argument("foo", location="get_json")
        self.assertEquals(arg.location, "get_json")

    def test_location_header_list(self):
        arg = Argument("foo", location=["headers"])
        self.assertEquals(arg.location, ["headers"])

    def test_type(self):
        arg = Argument("foo", type=int)
        self.assertEquals(arg.type, int)

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

    def test_convert_default_type_with_null_input(self):
        """convert() should properly handle case where input is None"""
        arg = Argument('foo')
        self.assertEquals(arg.convert(None), None)

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
    def testRequestParser_parse_addArgument(self):
        req = Request.blank("/bubble?foo=barß")
        parser = RequestParser()
        parser.add_argument(Argument("foo"))

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], u"barß")

    def testRequestParser_parse_unicode(self):
        req = Request.blank("/bubble?foo=barß")
        parser = RequestParser()
        parser.add_argument("foo")

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], u"barß")

    def testRequestParser_parse_append_ignore(self):
        req = Request.blank("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", ignore=True, type=int, action="append")

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], None)

    def testRequestParser_parse_append_default(self):
        req = Request.blank("/bubble?")

        parser = RequestParser()
        parser.add_argument("foo", action="append"),

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], None)

    def testRequestParser_parse_append(self):
        req = Request.blank("/bubble?foo=bar&foo=bat")

        parser = RequestParser()
        parser.add_argument("foo", action="append"),

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], ["bar", "bat"])

    def testRequestParser_parse_append_single(self):
        req = Request.blank("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", action="append"),

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], ["bar"])

    def testRequestParser_parse_dest(self):
        req = Request.blank("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", dest="bat")

        args = parser.parse_args(req)
        self.assertEquals(args['bat'], "bar")

    def testRequestParser_parse_required(self):
        req = Request.blank("/bubble")

        parser = RequestParser()
        parser.add_argument("foo", required=True)

        message = ''
        try:
            parser.parse_args(req)
        except MissingParameterError as e:
            message = e.message

        self.assertEquals(message, u'Missing required parameter foo in json or params')

        parser = RequestParser()
        parser.add_argument("bar", required=True, location=['values', 'cookies'])

        try:
            parser.parse_args(req)
        except Exception as e:
            message = e.message

        self.assertEquals(message, u"Missing required parameter bar in ['values', 'cookies']")

    def testRequestParser_default_append(self):
        req = Request.blank("/bubble")
        parser = RequestParser()
        parser.add_argument("foo", default="bar", action="append")

        args = parser.parse_args(req)

        self.assertEquals(args['foo'], "bar")

    def testRequestParser_default(self):
        req = Request.blank("/bubble")

        parser = RequestParser()
        parser.add_argument("foo", default="bar")

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], "bar")

    def testRequestParser_callable_default(self):
        req = Request.blank("/bubble")

        parser = RequestParser()
        parser.add_argument("foo", default=lambda: "bar")

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], "bar")

    def testRequestParser_none(self):
        req = Request.blank("/bubble")

        parser = RequestParser()
        parser.add_argument("foo")

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], None)

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

    def testRequestParser_type_is_decimal(self):
        import decimal

        parser = RequestParser()
        parser.add_argument("foo", type=decimal.Decimal, location="json")

        req = Request.blank('/stam', POST=json.dumps(dict(foo="1.0025")), environ={
            'CONTENT_TYPE': 'application/json;"',
        })
        args = parser.parse_args(req)
        self.assertEquals(args['foo'], decimal.Decimal("1.0025"))

    def testRequestParser_type_is_bool(self):
        import decimal

        parser = RequestParser()
        parser.add_argument("foo", type=bool)

        args = parser.parse_args(Request.blank('/stam?foo=true'))
        self.assertEquals(args['foo'], True)

        args = parser.parse_args(Request.blank('/stam?foo=True'))
        self.assertEquals(args['foo'], True)

        args = parser.parse_args(Request.blank('/stam?foo=t'))
        self.assertEquals(args['foo'], True)

        args = parser.parse_args(Request.blank('/stam?foo=1'))
        self.assertEquals(args['foo'], True)

        args = parser.parse_args(Request.blank('/stam?foo=f'))
        self.assertEquals(args['foo'], False)

        args = parser.parse_args(Request.blank('/stam?foo=0'))
        self.assertEquals(args['foo'], False)

        args = parser.parse_args(Request.blank('/stam?foo=false'))
        self.assertEquals(args['foo'], False)

        args = parser.parse_args(Request.blank('/stam?foo=False'))
        self.assertEquals(args['foo'], False)

    def testRequestParser_noParams_returnsNone(self):
        req = Request.blank('/')

        parser = RequestParser()
        parser.add_argument("foo")

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], None)

    def testRequestParser_choices_correct(self):
        req = Request.blank("/bubble?foo=bat")

        parser = RequestParser()
        parser.add_argument("foo", choices=["bat"]),

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], "bat")

    def testRequestParser_choices(self):
        req = Request.blank("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", choices=["bat"]),

        self.assertRaises(InvalidParameterValue, lambda: parser.parse_args(req))

    def testRequestParser_choices_sensitive(self):
        req = Request.blank("/bubble?foo=BAT")

        parser = RequestParser()
        parser.add_argument("foo", choices=["bat"], case_sensitive=True),

        self.assertRaises(InvalidParameterValue, lambda: parser.parse_args(req))

    def testRequestParser_choices_insensitive(self):
        req = Request.blank("/bubble?foo=BAT")

        parser = RequestParser()
        parser.add_argument("foo", choices=["bat"], case_sensitive=False),

        args = parser.parse_args(req)
        self.assertEquals('bat', args.get('foo'))

        # both choices and args are case_insensitive
        req = Request.blank("/bubble?foo=bat")

        parser = RequestParser()
        parser.add_argument("foo", choices=["BAT"], case_sensitive=False),

        args = parser.parse_args(req)
        self.assertEquals('bat', args.get('foo'))

    def testRequestParser_choices_types_int(self):
        parser = RequestParser()
        parser.add_argument("foo", type=int, choices=[1, 2, 3], location='json')

        req = Request.blank('/stam', POST=json.dumps(dict(foo=5)), environ={
            'CONTENT_TYPE': 'application/json;"',
        })

        self.assertRaises(InvalidParameterValue, parser.parse_args, req)

    def test_int_range_choice_types(self):
        parser = RequestParser()
        parser.add_argument("foo", type=int, choices=range(100), location='json')

        req = Request.blank('/stam', POST=json.dumps(dict(foo=101)), environ={
            'CONTENT_TYPE': 'application/json;"',
        })
        self.assertRaises(InvalidParameterValue, parser.parse_args, req)

        req = Request.blank('/stam', POST=json.dumps(dict(foo=99)), environ={
            'CONTENT_TYPE': 'application/json;"',
        })
        args = parser.parse_args(req)
        self.assertEqual(99, args.get('foo'))

    def testRequestParser_ignore(self):
        req = Request.blank("/bubble?foo=bar")

        parser = RequestParser()
        parser.add_argument("foo", type=int, ignore=True)

        args = parser.parse_args(req)
        self.assertEquals(args['foo'], None)

    def testRequestParser_noParamsWithDefault_returnsDefault(self):
        req = Request.blank('/')

        parser = RequestParser()
        parser.add_argument('foo', default='faa')

        args = parser.parse_args(req)
        self.assertEqual(args['foo'], 'faa')

    def testRequestParser_copy(self):
        req = Request.blank("/bubble?foo=101&bar=baz")
        parser = RequestParser()
        foo_arg = Argument('foo', type=int)
        parser.args.append(foo_arg)
        parser_copy = parser.copy()

        # Deepcopy should create a clone of the argument object instead of
        # copying a reference to the new args list
        self.assertFalse(foo_arg in parser_copy.args)

        # Args added to new parser should not be added to the original
        bar_arg = Argument('bar')
        parser_copy.args.append(bar_arg)
        self.assertFalse(bar_arg in parser.args)

        args = parser_copy.parse_args(req)
        self.assertEquals(args['foo'], 101)
        self.assertEquals(args['bar'], u'baz')

    def testRequestParser_replace_argument(self):
        req = Request.blank("/bubble?foo=baz")
        parser = RequestParser()
        parser.add_argument('foo', type=int)
        parser_copy = parser.copy()
        parser_copy.replace_argument('foo', type=str)

        args = parser_copy.parse_args(req)
        self.assertEquals(args['foo'], u'baz')

    # endregion
