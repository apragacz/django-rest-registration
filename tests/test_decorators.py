from collections.abc import Callable

from django.test import TestCase
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from rest_registration.decorators import serializer_class_getter


class SerializerClassGetterTestCase(TestCase):

    def setUp(self):
        self.decorator = serializer_class_getter(self._serializer_getter)

    def _dummy_view(self, request):
        return Response()

    def _serializer_getter(self):
        return Serializer

    def test_ok(self):
        input_view = (api_view(['GET']))(self._dummy_view)
        output_view = self.decorator(input_view)
        self.assertIsInstance(output_view, Callable)
        self.assertEqual(output_view.cls.get_serializer_class(), Serializer)

    def test_not_a_view(self):
        input_view = self._dummy_view
        self.assertRaises(Exception, lambda: self.decorator(input_view))
