from typing import Any, Dict, Optional, Sequence, Type

from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.metadata import BaseMetadata
from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.parsers import BaseParser
from rest_framework.permissions import BasePermission
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.settings import api_settings
from rest_framework.throttling import BaseThrottle
from rest_framework.versioning import BaseVersioning
from rest_framework.views import APIView


class BaseAPIView(APIView):
    renderer_classes: Optional[
        Sequence[Type[BaseRenderer]]] = None  # type: ignore
    parser_classes: Optional[
        Sequence[Type[BaseParser]]] = None  # type: ignore
    authentication_classes: Optional[
        Sequence[Type[BaseAuthentication]]] = None  # type: ignore
    throttle_classes: Optional[
        Sequence[Type[BaseThrottle]]] = None  # type: ignore
    permission_classes: Optional[
        Sequence[Type[BasePermission]]] = None  # type: ignore
    content_negotiation_class: Optional[
        Type[BaseContentNegotiation]] = None  # type: ignore
    metadata_class: Optional[Type[BaseMetadata]] = None  # type: ignore
    versioning_class: Optional[Type[BaseVersioning]] = None
    serializer_class: Optional[Type[Serializer]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._negotiator = None

    @property
    def default_response_headers(self):
        headers = {
            'Allow': ', '.join(self.allowed_methods),
        }
        if len(self.get_renderer_classes()) > 1:
            headers['Vary'] = 'Accept'
        return headers

    def get_renderers(self):
        """
        Instantiates and returns the list of renderers that this view can use.
        """
        return [renderer() for renderer in self.get_renderer_classes()]

    def get_renderer_classes(self):
        return _use_if_not_none(
            self.renderer_classes,
            api_settings.DEFAULT_RENDERER_CLASSES,
        )

    def get_parsers(self):
        """
        Instantiates and returns the list of parsers that this view can use.
        """
        return [parser() for parser in self.get_parser_classes()]

    def get_parser_classes(self):
        return _use_if_not_none(
            self.parser_classes,
            api_settings.DEFAULT_PARSER_CLASSES,
        )

    def get_authenticators(self):
        """
        Instantiates and returns the list of authenticators that this view can use.
        """
        return [auth() for auth in self.get_authentication_classes()]

    def get_authentication_classes(self):
        return _use_if_not_none(
            self.authentication_classes,
            api_settings.DEFAULT_AUTHENTICATION_CLASSES,
        )

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        return [permission() for permission in self.get_permission_classes()]

    def get_permission_classes(self):
        return _use_if_not_none(
            self.permission_classes,
            api_settings.DEFAULT_PERMISSION_CLASSES,
        )

    def get_throttles(self):
        """
        Instantiates and returns the list of throttles that this view uses.
        """
        return [throttle() for throttle in self.get_throttle_classes()]

    def get_throttle_classes(self):
        return _use_if_not_none(
            self.throttle_classes,
            api_settings.DEFAULT_THROTTLE_CLASSES,
        )

    def get_content_negotiator(self):
        """
        Instantiate and return the content negotiation class to use.
        """
        if not getattr(self, '_negotiator', None):
            content_negotiation_class = self.get_content_negotiation_class()
            self._negotiator = content_negotiation_class()
        return self._negotiator

    def get_content_negotiation_class(self):
        return _use_if_not_none(
            self.content_negotiation_class,
            api_settings.DEFAULT_CONTENT_NEGOTIATION_CLASS,
        )

    def options(self, request, *args, **kwargs):
        """
        Handler method for HTTP 'OPTIONS' request.
        """
        metadata_class = self.get_metadata_class()
        if metadata_class is None:
            return self.http_method_not_allowed(request, *args, **kwargs)
        data = metadata_class().determine_metadata(request, self)
        return Response(data, status=status.HTTP_200_OK)

    def get_metadata_class(self):
        return _use_if_not_none(
            self.metadata_class,
            api_settings.DEFAULT_METADATA_CLASS,
        )

    def determine_version(self, request, *args, **kwargs):
        """
        If versioning is being used, then determine any API version for the
        incoming request. Returns a two-tuple of (version, versioning_scheme)
        """
        versioning_class = self.get_versioning_class()
        if versioning_class is None:
            return (None, None)
        scheme = versioning_class()
        return (scheme.determine_version(request, *args, **kwargs), scheme)

    def get_versioning_class(self):
        return _use_if_not_none(
            self.versioning_class,
            api_settings.DEFAULT_VERSIONING_CLASS,
        )

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input.
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)  # pylint: disable=not-callable

    def get_serializer_class(self) -> Type[Serializer]:
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )

        return self.serializer_class

    def get_serializer_context(self) -> Dict[str, Any]:
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'view': self
        }


def _use_if_not_none(value, default):
    if value is None:
        return default
    return value
