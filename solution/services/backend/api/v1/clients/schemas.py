import typing
from uuid import UUID

from ninja import ModelSchema

from apps.client.models import Client


class Client(ModelSchema):
    client_id: UUID

    class Meta:
        model = Client
        exclude: typing.ClassVar[tuple[str]] = (Client.id.field.name,)
