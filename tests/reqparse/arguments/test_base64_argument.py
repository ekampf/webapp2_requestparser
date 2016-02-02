# -*- coding: utf-8 -*-
import base64
import unittest

from webapp2_restful.reqparse.arguments import Base64StringArgument

__author__ = 'ekampf'


class TestBase64Argument(unittest.TestCase):
    def setUp(self):
        self.target = Base64StringArgument()

    def testEmailArgument_invalidBase64_raisesValueError(self):
        with self.assertRaises(ValueError):
            expected = "I'm a value"
            self.target("abc"+base64.urlsafe_b64encode(expected))

    def testEmailArgument_validBase64_returnsDecodedValue(self):
        expected = "I'm a value"
        result = self.target(base64.urlsafe_b64encode(expected))
        self.assertEqual(expected, result)
