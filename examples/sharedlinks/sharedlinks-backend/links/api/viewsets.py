import logging

from django.contrib.auth.models import User
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import detail_route
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response

from links.models import Link, LinkVote

logger = logging.getLogger(__name__)


class NestedUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
        )


class LinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Link
        fields = (
            'id',
            'title',
            'url',
            'reporter',
            'vote_rank',
        )

    reporter = NestedUserSerializer(read_only=True)
    vote_rank = serializers.SerializerMethodField()

    def get_vote_rank(self, obj):
        num_of_pos_votes = obj.get_num_of_positive_votes()
        num_of_neg_votes = obj.get_num_of_negative_votes()
        return num_of_pos_votes - num_of_neg_votes


class LinkViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    queryset = Link.objects.all()
    serializer_class = LinkSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated()
        serializer.save(reporter=user)

    @detail_route(methods=['post'])
    def vote_up(self, request, pk):
        return self._vote(request, pk, {
            'positive': True,
            'negative': False,
        })

    @detail_route(methods=['post'])
    def vote_down(self, request, pk):
        return self._vote(request, pk, {
            'positive': False,
            'negative': True,
        })

    def _vote(self, request, pk, options):
        user = request.user
        if not user.is_authenticated:
            raise NotAuthenticated()
        vote, _ = LinkVote.objects.get_or_create(
            link_id=pk,
            voter=user,
            defaults=options,
        )
        for name, value in options.items():
            setattr(vote, name, value)
        vote.save()
        serializer = LinkSerializer(instance=vote.link)
        return Response(serializer.data)
