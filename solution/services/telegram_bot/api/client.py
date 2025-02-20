from http import HTTPStatus as status
from typing import Self

import httpx

import config
from api import errors, schemas


class AdNovaClient:
    def __init__(self) -> None:
        self.base_url = config.API_ENDPOINT

    async def __aenter__(self) -> Self:
        self.client = httpx.AsyncClient(base_url=self.base_url)
        return self

    async def __aexit__(
        self, exc_type: object, exc_val: object, exc_tb: object
    ) -> None:
        await self.client.aclose()

    def _handle_response(self, response: httpx.Response) -> httpx.Response:
        if response.status_code == status.BAD_REQUEST:
            error = schemas.BadRequestError.model_validate(response.json())
            raise errors.BadRequestError(error.detail)
        if response.status_code == status.FORBIDDEN:
            error = schemas.ForbiddenError.model_validate(response.json())
            raise errors.ForbiddenError(error.detail)
        if response.status_code == status.NOT_FOUND:
            error = schemas.NotFoundError.model_validate(response.json())
            raise errors.NotFoundError(error.detail)

        response.raise_for_status()

        return response

    def sync_get_advertiser(self, advertiser_id: str) -> schemas.Advertiser:
        client = httpx.Client(base_url=self.base_url)
        response = client.get(f"/advertisers/{advertiser_id}")
        self._handle_response(response)
        return schemas.Advertiser.model_validate(response.json())

    async def get_advertiser(self, advertiser_id: str) -> schemas.Advertiser:
        response = await self.client.get(f"/advertisers/{advertiser_id}")
        self._handle_response(response)
        return schemas.Advertiser.model_validate(response.json())

    async def create_campaign(
        self, advertiser_id: str, data: schemas.CampaignCreateIn
    ) -> schemas.CampaignOut:
        response = await self.client.post(
            f"/advertisers/{advertiser_id}/campaigns", json=data.model_dump()
        )
        self._handle_response(response)
        return schemas.CampaignOut.model_validate(response.json())

    async def list_campaigns(
        self, advertiser_id: str, page: int = 1, size: int = 1000
    ) -> list[schemas.CampaignOut]:
        params = {"page": page, "size": size}
        response = await self.client.get(
            f"/advertisers/{advertiser_id}/campaigns", params=params
        )
        self._handle_response(response)
        return [
            schemas.CampaignOut.model_validate(item)
            for item in response.json()
        ]

    async def get_campaign(
        self, advertiser_id: str, campaign_id: str
    ) -> schemas.CampaignOut:
        response = await self.client.get(
            f"/advertisers/{advertiser_id}/campaigns/{campaign_id}"
        )
        self._handle_response(response)
        return schemas.CampaignOut.model_validate(response.json())

    async def update_campaign(
        self,
        advertiser_id: str,
        campaign_id: str,
        data: schemas.CampaignUpdateIn,
    ) -> schemas.CampaignOut:
        response = await self.client.put(
            f"/advertisers/{advertiser_id}/campaigns/{campaign_id}",
            json=data.model_dump(),
        )
        self._handle_response(response)
        return schemas.CampaignOut.model_validate(response.json())

    async def delete_campaign(
        self, advertiser_id: str, campaign_id: str
    ) -> None:
        response = await self.client.delete(
            f"/advertisers/{advertiser_id}/campaigns/{campaign_id}"
        )
        self._handle_response(response)

    async def upload_ad_image(
        self, advertiser_id: str, campaign_id: str, file: bytes
    ) -> schemas.CampaignOut:
        files = {"ad_image": file}
        response = await self.client.post(
            f"/advertisers/{advertiser_id}/campaigns/{campaign_id}/ad_image",
            files=files,
        )
        self._handle_response(response)
        return schemas.CampaignOut.model_validate(response.json())

    async def delete_ad_image(
        self, advertiser_id: str, campaign_id: str
    ) -> None:
        response = await self.client.delete(
            f"/advertisers/{advertiser_id}/campaigns/{campaign_id}/ad_image"
        )
        self._handle_response(response)

    async def get_advertiser_statistics(
        self, advertiser_id: str
    ) -> schemas.Stat:
        response = await self.client.get(f"/stats/advertisers/{advertiser_id}")
        self._handle_response(response)
        return schemas.Stat.model_validate(response.json())

    async def get_daily_advertiser_statistics(
        self, advertiser_id: str
    ) -> list[schemas.DailyStat]:
        response = await self.client.get(
            f"/stats/advertisers/{advertiser_id}/daily"
        )
        self._handle_response(response)
        return [
            schemas.DailyStat.model_validate(item) for item in response.json()
        ]

    async def get_campaign_statistics(self, campaign_id: str) -> schemas.Stat:
        response = await self.client.get(f"/stats/campaigns/{campaign_id}")
        self._handle_response(response)
        return schemas.Stat.model_validate(response.json())

    async def get_daily_campaign_statistics(
        self, campaign_id: str
    ) -> list[schemas.DailyStat]:
        response = await self.client.get(
            f"/stats/campaigns/{campaign_id}/daily"
        )
        self._handle_response(response)
        return [
            schemas.DailyStat.model_validate(item) for item in response.json()
        ]

    async def generate_ad_text(
        self, data: schemas.GenerateAdTextIn
    ) -> schemas.GenerateAdTextResult:
        response = await self.client.post(
            "/generate/ad_text", json=data.model_dump()
        )
        self._handle_response(response)
        return schemas.GenerateAdTextResult.model_validate(response.json())

    async def get_generate_ad_text_result(
        self, task_id: str
    ) -> schemas.GenerateAdTextResult:
        response = await self.client.get(f"/generate/ad_text/{task_id}/result")
        self._handle_response(response)
        return schemas.GenerateAdTextResult.model_validate(response.json())
