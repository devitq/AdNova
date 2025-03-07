from django.contrib import admin

from apps.advertiser.models import Advertiser


class AdvertiserAdmin(admin.ModelAdmin):
    readonly_fields = (Advertiser.id.field.name,)
    fields = (
        Advertiser.id.field.name,
        Advertiser.name.field.name,
    )


admin.site.register(Advertiser, AdvertiserAdmin)
