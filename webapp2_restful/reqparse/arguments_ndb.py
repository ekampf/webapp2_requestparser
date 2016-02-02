# -*- coding: utf-8 -*-
import base64

try:
    from google.appengine.ext import ndb
except ImportError:
    raise Exception("NDB Required")

__author__ = 'ekampf'


class EntityIDArgument(object):
    def __init__(self, kind, key_only=False, is_base64=False):
        self.kind = kind
        self.key_only = key_only
        self.is_base64 = is_base64

    def __call__(self, entity_id):
        if self.is_base64:
            entity_id = base64.urlsafe_b64decode(str(entity_id))

        if self.key_only:
            return ndb.Key(self.kind, entity_id)
        else:
            return ndb.Key(self.kind, entity_id).get()


class EntityLongIDArgument(EntityIDArgument):
    def __call__(self, entity_id):
        return super(EntityLongIDArgument, self).__call__(long(entity_id))
