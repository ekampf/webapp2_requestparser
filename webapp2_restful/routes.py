from webapp2 import Route
from webapp2_extras.routes import MultiRoute

from inflection import singularize, pluralize

__author__ = 'ekampf'

# pylint:disable=C0326,R0902

class ResourceRoute(MultiRoute):
    ALL_REST_ACTIONS = ['index', 'create', 'show', 'update', 'destroy']

    def __init__(self, name, handler,
                 actions=None,
                 member_actions=None,
                 sub_resources=None,
                 only=None,
                 without=None,
                 path_prefix='',
                 name_prefix=''):

        """
        Defines routes for a RESTful resource.

        Example:

        >>> APP = WondermallWSGIApplication([
        >>>         ResourceRoute('photos', PhotosHandler, actions=[('delete_all', 'POST')], member_actions=['thumb'], sub_resources=[
        >>>             ResourceRoute('comments', PhotosCommentsHandler, only=['index', 'show'])
        >>>         ]
        >>> ])

        Creates the following routes:

          HTTP            PATH                                       Handler Method                   Name (uri_for)
        ----------------------------------------------------------------------------------------------------------------
        GET    - /photos                                - PhotosHandler.index(self)               - 'photos'
        POST   - /photos                                - PhotosHandler.create(self)              - 'photos'
        GET    - /photos/:photo_id                      - PhotosHandler.show(self, photo_id)      - 'photo'
        PUT    - /photos/:photo_id                      - PhotosHandler.update(self, photo_id)    - 'photo'
        DELETE - /photos/:photo_id                      - PhotosHandler.destroy(self, photo_id)   - 'photo'

        POST   - /photos/delete_all                     - PhotosHandler.delete_all                - 'photos_delete_all'
        GET    - /photos/:photo_id/thumb                - PhotosHandler.thumb(self, photo_id)     - 'photo_thumb'

        GET    - /photos/:photo_id/comments             - PhotosCommentsHandler.index(self)       - 'photo_comments'
        GET    - /photos/:photo_id/comments/:comment_id - PhotosCommentsHandler.show(self,        - 'photo_comment'
                                                                                     photo_id,
                                                                                     comment_id)


        :param name: The resource name. Has to be plural ('People', 'Posts', 'Users', ...)
        :param handler: The handler class to handle the resource
        :param actions: Additional actions that apply on the resource collection (all the resources of this type). An array of tuples (action_name, http_method) or just a name for GET actions
        :param member_actions: Additional action that apply to resource members (specific resource entities). An array of tuples (action_name, http_method) or just a name for GET actions
        :param sub_resources: An array of sub resources
        :param only: Specifies only to create specific REST routes. An array of strings with these possible values: ['index', 'create', 'show', 'update', 'destroy']
        :param without: Omit specific REST routes. An array of strings with these possible values: ['index', 'create', 'show', 'update', 'destroy']
        :param path_prefix: A path to prefix all teh resource's paths with. For example given '/api/v1' the resource's paths will be '/api/v1/photos' etc.
        :param name_prefix: A prefix to use for path name. For example: given 'api' the named routes would be 'api_photos', 'api_photo', etc.

        :type name: str
        :type handler: webapp2.RequestHandler
        :type actions: list[(str, str)|str]
        :type member_actions: list[(str, str)|str]
        :type sub_resources: list[ResourceRoute]

        :rtype: ResourceRoute
        """
        self.name = pluralize(name.lower())
        self.__handler = handler
        self.__actions = actions or []
        self.__member_actions = member_actions or []
        self.__sub_resources = sub_resources or []

        self.__path_prefix = path_prefix
        self.__name_prefix = name_prefix + '_' if name_prefix else ''

        self.supported_actions = only or self.ALL_REST_ACTIONS
        if without:
            self.supported_actions = [action for action in self.supported_actions if action not in without]

        # Make sure actions are (name, httml_method) tuples
        self.__actions        = [a if isinstance(a, tuple) else (str(a), 'GET') for a in self.__actions]
        self.__member_actions = [a if isinstance(a, tuple) else (str(a), 'GET') for a in self.__member_actions]

        routes = self.__get_routes()
        super(ResourceRoute, self).__init__(routes)

    def __get_routes(self):
        singular_name = singularize(self.name).replace('-', '_')
        resources_path = "%s/%s" % (self.__path_prefix, self.name)
        resource_path  = "%s/%s/<%s_id>" % (self.__path_prefix, self.name, singular_name)

        routes = []

        if "index" in self.supported_actions:
            routes.append(Route(resources_path, handler=self.__handler, methods=['GET', 'OPTIONS'], handler_method='index', name=self.__name_prefix + self.name))

        if "create" in self.supported_actions:
            routes.append(Route(resources_path, handler=self.__handler, methods=['POST', 'OPTIONS'], handler_method='create', name=self.__name_prefix + self.name))

        if "show" in self.supported_actions:
            routes.append(Route(resource_path,  handler=self.__handler, methods=['GET', 'OPTIONS'], handler_method='show', name=self.__name_prefix + singular_name))

        if "update" in self.supported_actions:
            routes.append(Route(resource_path,  handler=self.__handler, methods=['PUT', 'OPTIONS'], handler_method='update', name=self.__name_prefix + singular_name))

        if "destroy" in self.supported_actions:
            routes.append(Route(resource_path,  handler=self.__handler, methods=['DELETE', 'OPTIONS'], handler_method='destroy', name=self.__name_prefix + singular_name))

        for action_name, http_method in self.__actions:
            routes.append(Route(resources_path + '/' + action_name, handler=self.__handler, handler_method=action_name.replace('-', '_'), methods=['OPTIONS', http_method], name="%s_%s" % (self.__name_prefix + self.name, action_name)))

        for action_name, http_method in self.__member_actions:
            routes.append(Route(resource_path + '/' + action_name, handler=self.__handler, handler_method=action_name.replace('-', '_'), methods=['OPTIONS', http_method], name="%s_%s" % (self.__name_prefix + singular_name, action_name)))

        for sub in self.__sub_resources:
            for sub_route in sub.get_routes():
                routes.append(Route(resource_path + sub_route.template, handler=sub_route.handler, handler_method=sub_route.handler_method, methods=sub_route.methods, name="%s_%s" % (self.__name_prefix + singular_name, sub_route.name)))

        return routes
