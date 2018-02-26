from collections.abc import Callable

from django.test import TestCase
from rest_framework import serializers
from rest_framework.compat import uritemplate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from rest_registration.decorators import api_view_serializer_class_getter


class TestSerializer(Serializer):
    test_field = serializers.CharField()


class SerializerClassGetterTestCase(TestCase):

    def setUp(self):
        self.decorator = api_view_serializer_class_getter(
            self._serializer_getter)

    def _dummy_view(self, request):
        return Response()

    def _serializer_getter(self):
        return TestSerializer

    def test_ok(self):
        method = 'POST'
        input_view = (api_view([method]))(self._dummy_view)
        output_view = self.decorator(input_view)
        self.assertIsInstance(output_view, Callable)
        wrapper_cls = output_view.cls
        self.assertEqual(wrapper_cls.get_serializer_class(), TestSerializer)
        self.assertEqual(type(wrapper_cls.get_serializer()), TestSerializer)
        schema = wrapper_cls().schema
        # Ensure that get_link works properly.
        self.assertIsNotNone(uritemplate)
        link = schema.get_link('/api/dummy-view/', method, None)
        self.assertEqual(len(link.fields), 1)
        self.assertEqual(link.fields[0].name, 'test_field')
        self.assertTrue(link.fields[0].required)

    def test_not_a_view(self):
        input_view = self._dummy_view
        self.assertRaises(Exception, lambda: self.decorator(input_view))
