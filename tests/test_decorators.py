from collections.abc import Callable

from django.test import TestCase
from rest_framework import renderers
from rest_framework import request as rest_request
from rest_framework import serializers
from rest_framework.compat import uritemplate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.test import APIRequestFactory

from rest_registration.api import views
from rest_registration.decorators import api_view_serializer_class_getter


class ExampleSerializer(Serializer):
    test_field = serializers.CharField()


class SerializerClassGetterTestCase(TestCase):

    def setUp(self):
        self.decorator = api_view_serializer_class_getter(
            self._serializer_getter)

    def _dummy_view(self, request):
        return Response()

    def _serializer_getter(self):
        return ExampleSerializer

    def test_ok(self):
        method = 'POST'
        input_view = (api_view([method]))(self._dummy_view)
        output_view = self.decorator(input_view)
        self.assertIsInstance(output_view, Callable)
        wrapper_cls = output_view.cls
        self.assertEqual(wrapper_cls.get_serializer_class(), ExampleSerializer)
        self.assertEqual(type(wrapper_cls.get_serializer()), ExampleSerializer)
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

    def test_browsable_renderer_put_render(self):
        """
        Test, that PUT method works with BrowsableAPIRenderer
        This was not working in the past, because of `_get_serializer`
        didn't allow `instance parameter.
        """
        data = {'blah': 'blah'}
        method = 'PUT'
        request = rest_request.Request(APIRequestFactory().get('blah'))
        input_view = (api_view([method]))(self._dummy_view)
        output_view = self.decorator(input_view)
        wrapper_cls = output_view.cls
        test_view_instance = wrapper_cls()

        renderer = renderers.BrowsableAPIRenderer()
        renderer.accepted_media_type = None
        renderer.renderer_context = {}
        response = renderer.get_raw_data_form(
            data, test_view_instance, method, request,
        )
        self.assertEquals(response.data, {})

    def test_views_serializer_getter_returns_correct_value(self):
        view_list = [
            v for k, v in vars(views).items() if not k.startswith('_')]
        for view in view_list:
            serializer = view.cls.get_serializer()
            self.assertIsInstance(serializer, Serializer)
