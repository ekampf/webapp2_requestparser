# -*- coding: utf-8 -*-
import unittest

from webapp2_restful.reqparse import Argument
from webapp2_restful.reqparse.arguments import SafeStringArgument

__author__ = 'ekampf'


class TestStringArgument(unittest.TestCase):
    def setUp(self):
        self.target = Argument('test', type=SafeStringArgument())

    def testUnicodeValue(self):
        ustr = u'M·A·C'

        result = self.target.convert(ustr)
        self.assertEqual(result, ustr.encode('ascii', 'ignore'))

    def testRegularString(self):
        s = "test123"
        result = self.target.convert(s)
        self.assertEqual(result, s)
