# -*- coding: utf-8 -*-
import unittest

import json, jsonschema
from webapp2_restful.reqparse.arguments import JSONArgument

__author__ = 'ekampf'


# noinspection PyProtectedMember
class TestJSONArgument(unittest.TestCase):
    def setUp(self):
        self.target = JSONArgument()

    def test_none_returnsNone(self):
        self.assertIsNone(self.target(None))

    def test_validJSON_validObjectReturned(self):
        expected_obj = {'id': '1234', 'name': 'Jenna Jameson'}
        obj_json = json.dumps(expected_obj)

        actual_obj = self.target(obj_json)

        self.assertEqual(expected_obj, actual_obj)

    def test_invalidJSON_valueErrorRaised(self):
        obj_json = "{'id': , 'name': 'Jenna Jameson'}"
        with self.assertRaises(ValueError):
            self.target(obj_json)

    def test_validJSONWithMatchingSchema_validObjectReturned(self):
        expected_obj = {'id': '1234', 'name': 'Jenna Jameson'}
        obj_json = json.dumps(expected_obj)

        schema = {
            'type': 'object',
            'properties': {
                'id': {'type': 'string', 'minLength': 1},
                'name': {'type': 'string', 'minLength': 1}
            }
        }

        actual_obj = self.target(obj_json)
        self.assertEqual(expected_obj, actual_obj)

    def test_validJSONWithUnmatchingSchema_validationError(self):
        expected_obj = {'id': '1234', 'name': 'Jenna Jameson'}
        obj_json = json.dumps(expected_obj)

        schema = {
            'type': 'object',
            'properties': {
                'id': {'type': 'number'},
                'name': {'type': 'string', 'minLength': 1}
            }
        }

        target = JSONArgument(schema=schema)
        with self.assertRaises(jsonschema.ValidationError):
            target(obj_json)
