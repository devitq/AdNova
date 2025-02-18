# ruff: noqa: E501, W291
import logging

from django.conf import settings
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.exceptions import YCloudMLError

logger = logging.getLogger(__name__)

AD_PROMPT_TEMPLATE = """
Сгенерируй креативный рекламный текст для рекламодателя с именем: "{advertiser_name}", 
название рекламной кампании: "{ad_title}".

Требования:
1. Текст должен быть максимально привлекательным и продающим
2. Использовать современные маркетинговые приемы
3. Включить призыв к действию
4. Соблюдать структуру: заголовок - основной текст - заключение
5. Длина: 3-5 коротких предложений
6. Ответ должен содержать только текст рекламы без дополнительных комментариев
7. Весь текст должен быть на одной строчке

Пример хорошего текста:
"Запустите свой бизнес в космос с {{advertiser_name}}! Кампания "{{ad_title}}" предлагает 
уникальные решения для цифрового продвижения. Присоединяйтесь к лидерам рынка - получите 
персональную консультацию сегодня!"
""".strip()


class YandexAIAdTextGenerator:
    def __init__(self) -> None:
        self.sdk = YCloudML(
            folder_id=settings.YANDEX_CLOUD_FOLDER_ID,
            auth=settings.YANDEX_CLOUD_API_KEY,
        )

    def generate_ad_text(
        self, advertiser_name: str, ad_title: str
    ) -> str | None:
        try:
            prompt = AD_PROMPT_TEMPLATE.format(
                advertiser_name=advertiser_name, ad_title=ad_title
            )

            promise = (
                self.sdk.models.completions(
                    "yandexgpt-lite", model_version="latest"
                )
                .configure(max_tokens=400, temperature=0.9)
                .run_deferred([{"role": "system", "text": prompt}])
            )

            result = promise.wait()
            logger.debug("Generated ad text: %s", result)

            return self._clean_response(result.alternatives[0].text)

        except YCloudMLError:
            return None

    def _clean_response(self, text: str) -> str:
        cleaned = text.strip()
        cleaned = cleaned.replace('"', "")
        return " ".join(cleaned.splitlines())
