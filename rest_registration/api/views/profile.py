from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from rest_registration.decorators import api_view_serializer_class_getter
from rest_registration.settings import registration_settings


@api_view_serializer_class_getter(
    lambda: registration_settings.PROFILE_SERIALIZER_CLASS)
@api_view(['GET', 'POST', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request: Request) -> Response:
    '''
    Get or set user profile.
    '''
    serializer_class = registration_settings.PROFILE_SERIALIZER_CLASS
    if request.method in ['POST', 'PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = serializer_class(
            instance=request.user,
            data=request.data,
            partial=partial,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
    else:  # request.method == 'GET':
        serializer = serializer_class(
            instance=request.user,
            context={'request': request},
        )

    return Response(serializer.data)
