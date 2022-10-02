from typing import Type

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from rest_registration.api.views.base import BaseAPIView
from rest_registration.settings import registration_settings


class ProfileView(BaseAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self) -> Type[Serializer]:
        return registration_settings.PROFILE_SERIALIZER_CLASS

    def get(self, request: Request) -> Response:
        serializer = self.get_serializer(instance=request.user)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        return self._update_profile(request)

    def put(self, request: Request) -> Response:
        return self._update_profile(request)

    def patch(self, request: Request) -> Response:
        return self._update_profile(request, partial=True)

    def _update_profile(self, request: Request, partial: bool = False) -> Response:
        serializer = self.get_serializer(
            instance=request.user,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


profile = ProfileView.as_view()
