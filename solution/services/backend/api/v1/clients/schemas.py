import typing
from uuid import UUID

from ninja import ModelSchema

from apps.client.models import Client as ClientModel


class Client(ModelSchema):
    client_id: UUID

    class Meta:
        model = ClientModel
        exclude: typing.ClassVar[tuple[str]] = (ClientModel.id.field.name,)
