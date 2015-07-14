# -*- coding: utf-8 -*-
__author__ = 'ekampf'

import unittest

import json, jsonschema
from webapp2_requestparser.arguments import JSONArgument

# noinspection PyProtectedMember
class TestJSONArgument(unittest.TestCase):

    def test_validJson_validObjectReturned(self):
        expected_obj = {'id': '1234', 'name': 'Jenna Jameson'}
        obj_json = json.dumps(expected_obj)

        target = JSONArgument()

        actual_obj = target(obj_json)

        self.assertEqual(expected_obj, actual_obj)

    def test_invalidJson_valueErrorRaised(self):
        obj_json = "{'id': , 'name': 'Jenna Jameson'}"

        target = JSONArgument()

        with self.assertRaises(ValueError):
            target(obj_json)

    def test_validJsonWithMatchingSchema_validObjectReturned(self):
        expected_obj = {'id': '1234', 'name': 'Jenna Jameson'}
        obj_json = json.dumps(expected_obj)

        schema = {
            'type': 'object',
            'properties': {
                'id': {'type': 'string', 'minLength': 1},
                'name': {'type': 'string', 'minLength': 1}
            }
        }

        target = JSONArgument(schema)

        actual_obj = target(obj_json)

        self.assertEqual(expected_obj, actual_obj)

    def test_validJsonWithNotMatchingSchema_validationError(self):
        expected_obj = {'id': '1234', 'name': 'Jenna Jameson'}
        obj_json = json.dumps(expected_obj)

        schema = {
            'type': 'object',
            'properties': {
                'id': {'type': 'number'},
                'name': {'type': 'string', 'minLength': 1}
            }
        }

        target = JSONArgument(schema)

        with self.assertRaises(jsonschema.ValidationError):
            target(obj_json)
