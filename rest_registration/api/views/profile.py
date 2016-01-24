from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from rest_registration.settings import registration_settings


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    profile_serializer_class = registration_settings.PROFILE_SERIALIZER_CLASS
    profile_serializer = profile_serializer_class(instance=request.user)

    return Response(profile_serializer.data, status=status.HTTP_200_OK)
