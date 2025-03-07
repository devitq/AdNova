from typing import Any, Literal
from uuid import UUID

from ninja import Schema


class GenerateAdTextIn(Schema):
    advertiser_name: str
    ad_title: str


class Promise(Schema):
    task_id: UUID
    status: Literal[
        "PENDING",
        "RECEIVED",
        "STARTED",
        "SUCCESS",
        "FAILURE",
        "RETRY",
        "REVOKED",
    ]
    result: Any
