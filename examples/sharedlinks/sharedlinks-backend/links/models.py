from django.db import models
from django.contrib.auth.models import User


class Link(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=255)
    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='reported_links',
        null=True,
        blank=False,
    )

    def __str__(self):
        return f"{self.title} ({self.url})"

    def get_num_of_positive_votes(self):
        return self.votes.filter(positive=True).count()

    def get_num_of_negative_votes(self):
        return self.votes.filter(negative=True).count()


class LinkVote(models.Model):

    class Meta:
        unique_together = (
            ('link', 'voter'),
        )

    link = models.ForeignKey(
        Link,
        on_delete=models.CASCADE,
        related_name='votes',
    )
    voter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='votes',
        null=True,
        blank=False,
    )
    positive = models.BooleanField()
    negative = models.BooleanField()

    def __str__(self):
        if self.positive:
            vote = 'positive'
        elif self.negative:
            vote = 'negative'
        else:
            vote = 'neutral'

        return f"{vote} vote for {self.link} by {self.voter}"
