from django.contrib import admin

from apps.mlscore.models import Mlscore


class MlscoreAdmin(admin.ModelAdmin):
    readonly_fields = (Mlscore.id.field.name,)
    fields = (
        Mlscore.id.field.name,
        Mlscore.advertiser.field.name,
        Mlscore.client.field.name,
        Mlscore.score.field.name,
    )


admin.site.register(Mlscore, MlscoreAdmin)
