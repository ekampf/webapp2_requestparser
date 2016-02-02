# -*- coding: utf-8 -*-
import unittest
import webapp2
from webapp2_restful.routes import ResourceRoute

__author__ = 'ekampf'


class PhotosHandler(webapp2.RequestHandler):
    pass


class PhotosCommentsHandler(webapp2.RequestHandler):
    pass


class TestResourceRoute(unittest.TestCase):
    def testNameIsPluralLowercase(self):
        self.assertEqual('photos', ResourceRoute('photo', PhotosHandler).name)
        self.assertEqual('photos', ResourceRoute('Photo', PhotosHandler).name)
        self.assertEqual('photos', ResourceRoute('Photos', PhotosHandler).name)
        self.assertEqual('users', ResourceRoute('User', PhotosHandler).name)
        self.assertEqual('users', ResourceRoute('Users', PhotosHandler).name)

    def testBasicRestRoutes(self):
        r = ResourceRoute('photos', PhotosHandler, actions=[('delete_all', 'POST')], member_actions=['thumb'])
        router = webapp2.Router([r])

        # GET all
        route_match, args, kwargs = router.match(self.__blank('/photos'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'index')
        self.assertEqual(args, ())

        # POST
        route_match, args, kwargs = router.match(self.__blank('/photos', 'POST'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'create')
        self.assertEqual(args, ())

        # GET a specific resource
        route_match, args, kwargs = router.match(self.__blank('/photos/123'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'show')
        self.assertEqual(args, ())
        self.assertDictEqual(kwargs, dict(photo_id='123'))

        # DELETE a specific resource
        route_match, args, kwargs = router.match(self.__blank('/photos/123', 'DELETE'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'destroy')
        self.assertEqual(args, ())
        self.assertDictEqual(kwargs, dict(photo_id='123'))

        # PUT a specific resource
        route_match, args, kwargs = router.match(self.__blank('/photos/123', 'PUT'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'update')
        self.assertEqual(args, ())
        self.assertDictEqual(kwargs, dict(photo_id='123'))

        # Resource actions
        route_match, args, kwargs = router.match(self.__blank('/photos/delete_all', 'POST'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'delete_all')
        self.assertEqual(args, ())
        self.assertDictEqual(kwargs, dict())

        # Resource member actions
        route_match, args, kwargs = router.match(self.__blank('/photos/123/thumb'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'thumb')
        self.assertEqual(args, ())
        self.assertDictEqual(kwargs, dict(photo_id='123'))

    def testResourceWithMinusInName(self):
        r = ResourceRoute('ab-tests', PhotosHandler, actions=[('delete_all', 'POST')], member_actions=['thumb', 'scale-up'])
        router = webapp2.Router([r])

        # GET all
        route_match, args, kwargs = router.match(self.__blank('/ab-tests'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'index')
        self.assertEqual(args, ())

        # POST
        route_match, args, kwargs = router.match(self.__blank('/ab-tests', 'POST'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'create')
        self.assertEqual(args, ())

        # GET a specific resource
        route_match, args, kwargs = router.match(self.__blank('/ab-tests/123'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'show')
        self.assertEqual(args, ())
        self.assertDictEqual(kwargs, dict(ab_test_id='123'))

        # DELETE a specific resource
        route_match, args, kwargs = router.match(self.__blank('/ab-tests/123', 'DELETE'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'destroy')
        self.assertEqual(args, ())
        self.assertDictEqual(kwargs, dict(ab_test_id='123'))

        # PUT a specific resource
        route_match, args, kwargs = router.match(self.__blank('/ab-tests/123', 'PUT'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'update')
        self.assertEqual(args, ())
        self.assertDictEqual(kwargs, dict(ab_test_id='123'))

        # Resource actions
        route_match, args, kwargs = router.match(self.__blank('/ab-tests/delete_all', 'POST'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'delete_all')
        self.assertEqual(args, ())
        self.assertDictEqual(kwargs, dict())

        # Resource member actions
        route_match, args, kwargs = router.match(self.__blank('/ab-tests/123/thumb'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'thumb')
        self.assertEqual(args, ())
        self.assertDictEqual(kwargs, dict(ab_test_id='123'))

        route_match, args, kwargs = router.match(self.__blank('/ab-tests/123/scale-up'))
        self.assertEqual(route_match.handler, PhotosHandler)
        self.assertEqual(route_match.handler_method, 'scale_up')
        self.assertEqual(args, ())
        self.assertDictEqual(kwargs, dict(ab_test_id='123'))

    def testSubResources(self):
        r = ResourceRoute('photos', PhotosHandler, sub_resources=[
            ResourceRoute('comments', PhotosCommentsHandler)
        ])
        router = webapp2.Router([r])

        # GET all
        route_match, args, kwargs = router.match(self.__blank('/photos/123/comments/comm774'))
        self.assertEqual(route_match.handler, PhotosCommentsHandler)
        self.assertEqual(route_match.handler_method, 'show')
        self.assertEqual(args, ())
        self.assertDictEqual(kwargs, dict(photo_id='123', comment_id='comm774'))

    def testUriFor(self):
        class Handler(webapp2.RequestHandler):
            def get(self, *args, **kwargs):
                pass

        app = webapp2.WSGIApplication([
            ResourceRoute('photos', PhotosHandler, actions=[('delete_all', 'POST')], member_actions=['thumb'], sub_resources=[
                ResourceRoute('comments', PhotosCommentsHandler)
            ])
        ])

        req = webapp2.Request.blank('http://localhost:80/')
        req.route = webapp2.Route('')
        req.route_args = tuple()
        req.route_kwargs = {}
        req.app = app
        app.set_globals(app=app, request=req)
        handler = Handler(req, webapp2.Response())
        handler.app = app

        for func in (handler.uri_for,):
            self.assertEqual(func('photos'), '/photos')
            self.assertEqual(func('photo', photo_id=123), '/photos/123')
            self.assertEqual(func('photo_comments', photo_id=123), '/photos/123/comments')
            self.assertEqual(func('photo_comment', photo_id=123, comment_id='bla'), '/photos/123/comments/bla')

    def __blank(self, path, method=None):
        req = webapp2.Request.blank(path)
        if method:
            req.method = method

        return req
