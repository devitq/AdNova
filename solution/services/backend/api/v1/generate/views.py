from http import HTTPStatus as status
from uuid import UUID

import celery.states
from celery.result import AsyncResult
from django.http import Http404, HttpRequest
from ninja import Router

from api.v1 import schemas as global_schemas
from api.v1.generate import schemas
from apps.campaign.tasks import generate_ad_text_task

router = Router(tags=["generate"])


@router.post(
    "/ad_text",
    response={
        status.OK: schemas.Promise,
        status.BAD_REQUEST: global_schemas.BadRequestError,
    },
)
def generate_ad_text(
    request: HttpRequest, prompt: schemas.GenerateAdTextIn
) -> tuple[status, schemas.Promise]:
    task = generate_ad_text_task.delay(prompt.advertiser_name, prompt.ad_title)
    task_result = AsyncResult(task.id)

    return status.OK, schemas.Promise(
        task_id=task.id,
        status=task_result.status,
        result=task_result.result,
    )


@router.get(
    "/ad_text/{task_id}/result",
    response={
        status.OK: schemas.Promise,
        status.BAD_REQUEST: global_schemas.BadRequestError,
        status.NOT_FOUND: global_schemas.NotFoundError,
    },
)
def get_generate_ad_text_result(
    request: HttpRequest, task_id: UUID
) -> tuple[status, schemas.Promise]:
    task_result = AsyncResult(str(task_id))

    if task_result.status == celery.states.PENDING:
        raise Http404

    return status.OK, schemas.Promise(
        task_id=task_result.task_id,
        status=task_result.status,
        result=task_result.result,
    )
