# -*- coding: utf-8 -*-
__author__ = 'ekampf'

import base64
import re
import json
from datetime import datetime
import jsonschema

class DateStringArgument(object):
    def __init__(self, date_format='%Y-%m-%d %H:%M:%S%f'):
        self.date_format = date_format

    def __call__(self, in_date):
        try:
            date = datetime.strptime(in_date, self.date_format)
        except ValueError, v:
            if len(v.args) > 0 and v.args[0].startswith('unconverted data remains: '):
                date = in_date[:-(len(v.args[0])-26)]
                date = datetime.strptime(date, self.date_format)
            else:
                raise ValueError('date cannot be created from string %s' % in_date)
        return date


class JSONArgument(object):
    def __init__(self, schema=None):
        self.schema = schema

    def __call__(self, json_str):
        if json_str is None:
            return None

        if isinstance(json_str, basestring):
            json_obj = json.loads(json_str)
        else:
            json_obj = json_str

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


class Base64String(object):
    def __call__(self, s):
        return base64.urlsafe_b64decode(str(s))


class SafeStringArgument(object):
    """
    Like a simple str argument but handles unicode input by stripping it...
    """
    def __call__(self, s):
        if isinstance(s, unicode):
            return s.encode('ascii', 'ignore')

        return s
