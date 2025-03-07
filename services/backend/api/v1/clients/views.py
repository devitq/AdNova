from collections import defaultdict
from http import HTTPStatus as status
from uuid import UUID

from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from api.v1 import schemas as global_schemas
from api.v1.clients import schemas
from apps.client.models import Client

router = Router(tags=["clients"])


@router.post(
    "/bulk",
    response={
        status.CREATED: list[schemas.Client],
        status.BAD_REQUEST: global_schemas.BadRequestError,
    },
)
def bulk_create_or_update(
    request: HttpRequest, data: list[schemas.Client]
) -> tuple[status, list[Client]]:
    latest_clients = defaultdict(lambda: None)

    for item in reversed(data):
        Client(id=item.client_id, **item.dict(exclude={"client_id"})).validate(
            validate_unique=False,
            validate_constraints=False,
        )
        if latest_clients[item.client_id] is None:
            latest_clients[item.client_id] = item

    unique_clients = reversed(list(latest_clients.values()))

    result = []

    with transaction.atomic():
        for client in unique_clients:
            client_instance, _ = Client.objects.update_or_create(
                id=client.client_id,
                defaults={**dict(client)},
            )
            result.append(client_instance)

    return status.CREATED, result


@router.get(
    "/{client_id}",
    response={
        status.OK: schemas.Client,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def get_client(
    request: HttpRequest, client_id: UUID
) -> tuple[status, schemas.Client]:
    return status.OK, get_object_or_404(Client, id=client_id)
