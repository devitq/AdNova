from collections import defaultdict
from http import HTTPStatus as status
from uuid import UUID

from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from api.v1 import schemas as global_schemas
from api.v1.advertisers import schemas
from apps.advertiser.models import Advertiser
from apps.mlscore.models import Mlscore

router = Router(tags=["advertisers"])


@router.post(
    "/ml-scores",
    response={
        status.OK: schemas.Mlscore,
        status.BAD_REQUEST: global_schemas.BadRequestError,
    },
)
def create_or_update_mlscore(
    request: HttpRequest, mlscore: schemas.Mlscore
) -> tuple[status, schemas.Mlscore]:
    mlscore_instance, _ = Mlscore.objects.update_or_create(
        advertiser_id=mlscore.advertiser,
        client_id=mlscore.client,
        defaults={"score": mlscore.score},
    )

    return status.OK, mlscore_instance


@router.post(
    "/bulk",
    response={
        status.CREATED: list[schemas.Advertiser],
        status.BAD_REQUEST: global_schemas.BadRequestError,
    },
)
def bulk_create_or_update(
    request: HttpRequest, data: list[schemas.Advertiser]
) -> tuple[status, list[Advertiser]]:
    latest_advertisers: dict[UUID, schemas.Advertiser] = defaultdict(
        lambda: None
    )

    for item in reversed(data):
        if latest_advertisers[item.advertiser_id] is None:
            Advertiser(
                id=item.advertiser_id, **item.dict(exclude={"client_id"})
            ).validate(
                validate_unique=False,
                validate_constraints=False,
            )
            latest_advertisers[item.advertiser_id] = item

    unique_advertisers = reversed(list(latest_advertisers.values()))

    result = []

    with transaction.atomic():
        for advertiser in unique_advertisers:
            advertiser_instance, _ = Advertiser.objects.update_or_create(
                id=advertiser.advertiser_id,
                defaults={**dict(advertiser)},
            )
            result.append(advertiser_instance)

    return status.CREATED, result


@router.get(
    "/{advertiser_id}",
    response={
        status.OK: schemas.Advertiser,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def get_advertiser(
    request: HttpRequest, advertiser_id: UUID
) -> tuple[status, Advertiser]:
    return status.OK, get_object_or_404(Advertiser, id=advertiser_id)
