from rest_framework import routers

from links.api.viewsets import LinkViewSet


router = routers.SimpleRouter()
router.register(r'links', LinkViewSet, base_name='link')

urlpatterns = router.urls
