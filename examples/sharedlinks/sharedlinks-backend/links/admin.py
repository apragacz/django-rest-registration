from django.contrib import admin

from links.models import Link, LinkVote


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    pass


@admin.register(LinkVote)
class LinkVoteAdmin(admin.ModelAdmin):
    pass
