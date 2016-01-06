from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .base import get_profile_serializer_class


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def profile(request):
    profile_serializer_class = get_profile_serializer_class()
    profile_serializer = profile_serializer_class(instance=request.user)

    return Response(profile_serializer.data, status=status.HTTP_201_CREATED)
