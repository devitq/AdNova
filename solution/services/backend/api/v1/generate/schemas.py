from typing import Any

from ninja import Schema


class GenerateAdTextIn(Schema):
    advertiser_name: str
    ad_title: str


class Promise(Schema):
    task_id: str
    status: str
    result: Any
