from django.contrib import admin

from apps.client.models import Client


class ClientAdmin(admin.ModelAdmin):
    readonly_fields = (Client.id.field.name,)
    fields = (
        Client.id.field.name,
        Client.login.field.name,
        Client.age.field.name,
        Client.location.field.name,
        Client.gender.field.name,
    )


admin.site.register(Client, ClientAdmin)
