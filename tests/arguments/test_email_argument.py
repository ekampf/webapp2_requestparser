# -*- coding: utf-8 -*-
__author__ = 'ekampf'

import unittest
from mock import Mock, NonCallableMock
from webapp2 import Request

from webapp2_requestparser.arguments import EmailArgument

class TestEmailArgument(unittest.TestCase):
    def setUp(self):
        self.target = EmailArgument()

    def testEmailArgument_NoAtEmail_throwsValueError(self):
        with self.assertRaises(ValueError):
            self.target("invalid_email")

    def testEmailArgument_TwoWordsEmail_throwsValueError(self):
        with self.assertRaises(ValueError):
            self.target("eran@ekampf")

    def testEmailArgument_TwoAtEmail_throwsValueError(self):
        with self.assertRaises(ValueError):
            self.target("eran@@ekampf.com")

    def testEmailArgument_WithSpaceEmail_throwsValueError(self):
        with self.assertRaises(ValueError):
            self.target("er ran@@ekampf.com")

    def testRequestParser_validEmail_returnsValue(self):
        self.target("eran@ekampf.com")

    def testRequestParser_PointInEmail_returnsValue(self):
        self.target("eran.kampf@whatever.com")

    def testRequestParser_UpperCaseEmail_returnsValue(self):
        self.target("ERAN@EKAMPF.COM")
