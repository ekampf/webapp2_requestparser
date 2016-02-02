# -*- coding: utf-8 -*-
import unittest

from webapp2_restful.reqparse.arguments import DateStringArgument

__author__ = 'ekampf'


class TestDateStringArgument(unittest.TestCase):
    def test_default_format_valid(self):
        target = DateStringArgument()
        dt = target('2015-07-16 08:34:57700140')
        self.assertEqual(dt.year, 2015)
        self.assertEqual(dt.month, 7)
        self.assertEqual(dt.day, 16)
        self.assertEqual(dt.hour, 8)
        self.assertEqual(dt.minute, 34)
