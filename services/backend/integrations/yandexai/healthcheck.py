from django.conf import settings
from health_check.backends import BaseHealthCheckBackend
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.exceptions import YCloudMLError


class YandexAIHealthCheck(BaseHealthCheckBackend):
    critical_service = False

    def check_status(self) -> None:
        try:
            sdk = YCloudML(
                folder_id=settings.YANDEX_CLOUD_FOLDER_ID,
                auth=settings.YANDEX_CLOUD_API_KEY,
            )
            result = sdk.models.completions(
                "yandexgpt-lite", model_version="latest"
            ).tokenize("ping")

            if not result:
                self.add_error("YandexAI API is unaccessible")

        except YCloudMLError:
            self.add_error("YandexAI API is unaccessible")

    def identifier(self) -> str:
        return self.__class__.__name__
