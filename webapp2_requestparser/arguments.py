# -*- coding: utf-8 -*-
import base64
import re
import json
from datetime import datetime
import jsonschema

__author__ = 'ekampf'


class DateStringArgument(object):
    def __init__(self, date_format='%Y-%m-%d %H:%M:%S%f'):
        self.date_format = date_format

    def __call__(self, in_date):
        return datetime.strptime(in_date, self.date_format)


class JSONArgument(object):
    def __init__(self, schema=None):
        self.schema = schema

    def __call__(self, json_str):
        if json_str is None:
            return None

        json_obj = json.loads(json_str)
        if self.schema is not None:
            jsonschema.validate(json_obj, self.schema)

        return json_obj


class EmailArgument(object):
    def __init__(self, email_regex='^[a-z0-9!#$%&''*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&''*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$'):
        self.email_regex = email_regex

    def __call__(self, email):
        if not re.match(self.email_regex, email.lower()):
            raise ValueError('Invalid email address %s' % email)

        return email.lower()


class Base64StringArgument(object):
    def __call__(self, s):
        try:
            return base64.urlsafe_b64decode(str(s))
        except Exception as ex:
            raise ValueError("Invalid base 64 value. %s" % ex.message)


class SafeStringArgument(object):
    """
    Like a simple str argument but handles unicode input by stripping it...
    """
    def __call__(self, s):
        if isinstance(s, unicode):
            return s.encode('ascii', 'ignore')

        return s
