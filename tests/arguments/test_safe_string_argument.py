# -*- coding: utf-8 -*-
__author__ = 'ekampf'

import unittest
from mock import Mock, NonCallableMock
from webapp2 import Request

from webapp2_requestparser.parser import Argument
from webapp2_requestparser.arguments import SafeStringArgument


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

