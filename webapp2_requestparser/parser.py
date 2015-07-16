# -*- coding: utf-8 -*-
__author__ = 'ekampf'

import inspect
import decimal

from webob.multidict import MultiDict


class ParserError(Exception):
    def __init__(self, argument):
        message = "Error parsing argument %s. %s" % (argument.name, argument.help or '')
        super(ParserError, self).__init__(self, message)


class MissingParameterError(ParserError):
    MISSING_PARAMETER_FORMAT = u'Missing required parameter {0} in {1}'

    def __init__(self, argument):
        ParserError.__init__(self, argument)
        if isinstance(argument.location, basestring):
            self.message = self.MISSING_PARAMETER_FORMAT.format(
                argument.name, _friendly_location.get(argument.location, argument.location))
        elif isinstance(argument.location, list):
            self.message = self.MISSING_PARAMETER_FORMAT.format(argument.name, argument.location)
        else:
            friendly_locations = [_friendly_location.get(loc, loc) for loc in argument.location]
            self.message = self.MISSING_PARAMETER_FORMAT.format(argument.name, ' or '.join(friendly_locations))


class InvalidParameterValue(ParserError):
    def __init__(self, argument, value, inner_error_message):
        ParserError.__init__(self, argument)
        self.message = "Invalid value for %s: %s (%s). %s" % (
            argument.name, value, inner_error_message, argument.help or '')


class InvalidChoiceParameterValue(InvalidParameterValue):
    def __init__(self, argument, value):
        InvalidParameterValue.__init__(self, argument, value, "%s is not a valid choice value" % value)


_friendly_location = {
    u'form': u'the post body',
    u'args': u'the query string',
    u'values': u'the post body or the query string',
    u'headers': u'the HTTP headers',
    u'cookies': u'the request\'s cookies',
    u'files': u'an uploaded file',
}


class Namespace(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


# pylint: disable=R0902
class Argument(object):
    # pylint: disable=W0622
    def __init__(self, name, default=None, dest=None, required=False, ignore=False,
                 type=unicode, location=('json', 'params',),
                 choices=(), action='store', help=None,
                 case_sensitive=True, trim=False):
        """
        :param name: Either a name or a list of option strings, e.g. foo or -f, --foo.
        :param default: The value produced if the argument is absent from the request.
        :param dest: The name of the attribute to be added to the object returned by parse_args(req).
        :param bool required: Whether or not the argument may be omitted (optionals only).
        :param ignore: Whether to ignore cases where the argument fails type conversion
        :param type: The type to which the request argument should be converted. If a type raises a ValidationError, the message in the error will be returned in the response.
        :param location: Where to source the arguments from the web request (ex: headers, args, etc.), can be an iterator, can also be dict with values inside the iterator.
        :param choices: A container of the allowable values for the argument.
        :param action: The basic type of action to be taken when this argument is encountered in the request.
        :param help: A brief description of the argument, returned in the response when the argument is invalid. This takes precedence over the message passed to a ValidationError raised by a type converter.
        :param bool case_sensitive: Whether the arguments in the request are case sensitive or not
        :param bool trim: If enabled, trims whitespace around the argument.
        """
        self.name = name
        self.default = default
        self.dest = dest
        self.required = required
        self.ignore = ignore
        self.location = location
        self.type = type
        self.choices = choices
        self.action = action
        self.help = help
        self.case_sensitive = case_sensitive
        self.trim = trim

    # noinspection PyBroadException
    # pylint: disable=E0110, W0702
    def source(self, request):
        """Pulls values off the request in the provided location
        :param request: The request object
        """
        if isinstance(self.location, basestring):
            value = getattr(request, self.location, MultiDict())
            if callable(value):
                value = value()

            if value is not None:
                return value
        else:
            for l in self.location:
                if isinstance(l, dict) or isinstance(l, MultiDict):
                    value = l
                else:
                    try:
                        value = getattr(request, l, None)
                    except:
                        continue

                if callable(value):
                    value = value()

                if value is not None:
                    return value

        return MultiDict()

    def convert(self, value):
        # Check if we're expecting a string and the value is None
        if value is None and inspect.isclass(self.type) and issubclass(self.type, basestring):
            return None

        try:
            if self.type is bool:
                return str(value) in ['True', 'true', '1', 't', 'y', 'yes']
            elif self.type is decimal.Decimal:
                return self.type(str(value), self.name)
            else:
                return self.type(value, self.name)
        except TypeError:
            return self.type(value)

    def parse(self, request):
        results = self.__parse_results(self.source(request))

        if not results and self.required:
            raise MissingParameterError(self)

        if not results:
            if callable(self.default):
                return self.default()
            else:
                return self.default

        if self.action == 'append':
            return results

        if self.action == 'store' or len(results) == 1:
            return results[0]

        return results

    def __parse_results(self, source, include_none=False):
        if hasattr(source, "getlist"):
            values = source.getlist(self.name)
        elif hasattr(source, "getall"):
            values = source.getall(self.name)
        else:
            values = [source.get(self.name)]

        results = []
        for value in values:
            if hasattr(value, "strip") and self.trim:
                value = value.strip()

            if hasattr(value, "lower") and not self.case_sensitive:
                value = value.lower()
                if hasattr(self.choices, "__iter__"):
                    self.choices = [choice.lower() for choice in self.choices]

            try:
                if value is not None:
                    value = self.convert(value)
            except Exception as error:
                if value is None or self.ignore:
                    continue
                raise InvalidParameterValue(self, value, str(error))

            if self.choices and value not in self.choices:
                raise InvalidChoiceParameterValue(self, value)

            results.append(value)

        return [result for result in results if result is not None or include_none]


class RequestParser(object):
    """Enables adding and parsing of multiple arguments in the context of a
        single request. Ex::

        parser = RequestParser()
        parser.add_argument('foo')
        parser.add_argument('int_bar', type=int)
        args = parser.parse_args()
        """

    def __init__(self, argument_class=Argument, namespace_class=Namespace):
        self.args = []
        self.argument_class = argument_class
        self.namespace_class = namespace_class

    def add_argument(self, *args, **kwargs):
        """Adds an argument to be parsed.

            Accepts either a single instance of Argument or arguments to be passed
            into :class:`Argument`'s constructor.

            See :class:`Argument`'s constructor for documentation on the
            available options.
            """
        if len(args) == 1 and isinstance(args[0], self.argument_class):
            self.args.append(args[0])
        else:
            self.args.append(self.argument_class(*args, **kwargs))
        return self

    def parse_args(self, request):
        results = self.namespace_class()

        for arg in self.args:
            value = arg.parse(request)
            key = arg.dest or arg.name
            results[key] = value

        return results

    def copy(self):
        """ Creates a copy of this RequestParser with the same set of arguments """
        parser_copy = RequestParser(self.argument_class, self.namespace_class)
        parser_copy.args = list(self.args)
        return parser_copy

    def replace_argument(self, name, *args, **kwargs):
        """ Replace the argument matching the given name with a new version. """
        new_arg = self.argument_class(name, *args, **kwargs)
        for index, arg in enumerate(self.args[:]):
            if new_arg.name == arg.name:
                del self.args[index]
                self.args.append(new_arg)
                break
        return self

