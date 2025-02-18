# ruff: noqa: E501, W291
import logging

from django.conf import settings
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.exceptions import YCloudMLError

logger = logging.getLogger(__name__)

DEFAULT_INVALID_SIGNAL = (
    "В интернете есть много сайтов с информацией на эту тему. "
    "[Посмотрите, что нашлось в поиске](https://ya.ru)"
).lower()

MODERATION_PROMPT = """
Ты — строгий AI-модератор контента. Анализируй текст ПО ВСЕМ указанным критериям.
Если ЛЮБОЙ из критериев нарушен — верни true. Только если ВСЕ критерии соблюдены — верни false.

Критерии нарушений (true):
1. Нецензурная лексика: мат, эвфемизмы, оскорбительные выражения
2. Угрозы: прямые/косвенные угрозы жизни, шантаж, буллинг
3. Дискриминация: расизм, сексизм, ксенофобия, гомофобия
""".strip()


class YandexAIModerator:
    def __init__(self) -> None:
        self.sdk = YCloudML(
            folder_id=settings.YANDEX_CLOUD_FOLDER_ID,
            auth=settings.YANDEX_CLOUD_API_KEY,
        )

    def get_moderation_verdict(self, text: str) -> bool:
        try:
            promise = (
                self.sdk.models.completions(
                    "yandexgpt-lite", model_version="latest"
                )
                .configure(max_tokens=200, temperature=0.1)
                .run_deferred(
                    [
                        {"role": "system", "text": MODERATION_PROMPT},
                        {"role": "user", "text": text},
                    ]
                )
            )
            result = promise.wait()
            logger.debug("Moderation API response: %s", result)

            return self._normalize_response(result.alternatives[0].text)

        except YCloudMLError:
            return False

    def _normalize_response(self, text: str) -> bool:
        clean_verdict = text.strip().lower().split("\n")[0]
        return clean_verdict in ("true", DEFAULT_INVALID_SIGNAL)
