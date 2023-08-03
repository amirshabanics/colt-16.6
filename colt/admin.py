from django.contrib import admin
from colt.models import Game, Section, User


class UserInline(admin.TabularInline):
    model = User


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    pass
    # inlines = [UserInline]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    pass
    # inlines = [UserInline]
