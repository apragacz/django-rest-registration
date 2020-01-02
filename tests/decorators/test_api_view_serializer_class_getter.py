from collections.abc import Callable

import pytest
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
from tests.helpers.api_views import rest_framework_version_info  # noqa: F401


class ExampleSerializer(Serializer):  # pylint: disable=abstract-method
    test_field = serializers.CharField()


@pytest.fixture()
def decorator():
    return api_view_serializer_class_getter(lambda: ExampleSerializer)


@pytest.fixture()
def input_post_view():
    return (api_view(['POST']))(dummy_view_func)


@pytest.fixture()
def input_put_view():
    return (api_view(['PUT']))(dummy_view_func)


def test_success(input_post_view, decorator):
    output_view = decorator(input_post_view)
    assert isinstance(output_view, Callable)
    wrapper_cls = _get_view_class(output_view)
    assert wrapper_cls.get_serializer_class() == ExampleSerializer
    assert isinstance(wrapper_cls.get_serializer(), ExampleSerializer)


@pytest.mark.skipif('rest_framework_version_info < (3, 10, 0)')
def test_default_schema_success(input_post_view, decorator):
    output_view = decorator(input_post_view)
    wrapper_cls = _get_view_class(output_view)

    schema = wrapper_cls().schema
    operation = schema.get_operation('/api/dummy-view/', 'POST')
    operation_schema = operation['requestBody']['content']['application/json']['schema']  # noqa: E501
    expected_operation_schema = {
        'properties': {
            'test_field': {'type': 'string'},
        },
        'required': ['test_field'],
    }
    assert operation_schema == expected_operation_schema


@pytest.mark.skipif('rest_framework_version_info < (3, 10, 0)')
def test_coreapi_autoschema_success(
        settings_with_coreapi_autoschema, input_post_view, decorator):
    output_view = decorator(input_post_view)
    wrapper_cls = _get_view_class(output_view)

    schema = wrapper_cls().schema
    # Ensure that get_link works properly with coreapi AutoSchema
    assert uritemplate is not None
    link = schema.get_link('/api/dummy-view/', 'POST', None)
    assert len(link.fields) == 1
    assert link.fields[0].name == 'test_field'
    assert link.fields[0].required


@pytest.mark.skipif('rest_framework_version_info >= (3, 10, 0)')
def test_default_schema_success_deprecated(input_post_view, decorator):
    output_view = decorator(input_post_view)
    wrapper_cls = _get_view_class(output_view)

    schema = wrapper_cls().schema
    # Ensure that get_link works properly with coreapi AutoSchema
    assert uritemplate is not None
    link = schema.get_link('/api/dummy-view/', 'POST', None)
    assert len(link.fields) == 1
    assert link.fields[0].name == 'test_field'
    assert link.fields[0].required


def test_not_a_view(decorator):
    with pytest.raises(Exception):
        decorator(dummy_view_func)


def test_browsable_renderer_put_render(input_put_view, decorator):
    """
    Test, that PUT method works with BrowsableAPIRenderer
    This was not working in the past, because of `_get_serializer`
    didn't allow `instance parameter.
    """
    data = {'blah': 'blah'}
    method = 'PUT'
    request = rest_request.Request(APIRequestFactory().get('blah'))
    output_view = decorator(input_put_view)
    wrapper_cls = _get_view_class(output_view)
    test_view_instance = wrapper_cls()

    renderer = renderers.BrowsableAPIRenderer()
    renderer.accepted_media_type = None
    renderer.renderer_context = {}
    response = renderer.get_raw_data_form(
        data, test_view_instance, method, request,
    )
    assert response.data == {}


def test_views_serializer_getter_returns_correct_value():
    view_list = [
        v for k, v in vars(views).items() if not k.startswith('_')]
    for view in view_list:
        serializer = view.cls.get_serializer()
        assert isinstance(serializer, Serializer)


def dummy_view_func(request):
    return Response()


def _get_view_class(view):
    return view.cls
