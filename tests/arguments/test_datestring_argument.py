# -*- coding: utf-8 -*-
__author__ = 'ekampf'

import base64
import unittest

from webapp2_requestparser.arguments import DateStringArgument

class TestDateStringArgument(unittest.TestCase):

    def test_default_format_valid(self):
        target = DateStringArgument()
        dt = target('2015-07-16 08:34:57700140')
        self.assertEqual(dt.year, 2015)
        self.assertEqual(dt.month, 7)
        self.assertEqual(dt.day, 16)
        self.assertEqual(dt.hour, 8)
        self.assertEqual(dt.minute, 34)

