import logging
import time
from http import HTTPStatus as status

from httpx import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_generate_ad_text(client: Client) -> None:
    """
    Tests integration between:
    - backend
    - redis
    - yandexgpt
    - celery
    """

    payload = {
        "advertiser_name": "Центральный Университет",
        "ad_title": "Всероссийский кейс-чемпионат DEADLINE",
    }
    response = client.post("/generate/ad_text", json=payload)
    assert response.status_code == status.OK

    response_data = response.json()
    assert "task_id" in response_data, "Missing task_id in response"

    task_id = response_data["task_id"]
    start_time = time.time()

    while True:
        result_response = client.get(f"/generate/ad_text/{task_id}/result")
        assert result_response.status_code in (status.OK, status.NOT_FOUND)
        result_data = result_response.json()

        if (
            result_data.get("status") == "SUCCESS"
            and result_response.status_code == status.OK
        ):
            assert isinstance(result_data.get("result"), str), (
                "Result must be a string"
            )
            elapsed_time = time.time() - start_time
            logger.info(
                "Task %s completed in %.2f seconds", task_id, elapsed_time
            )
            logger.info("Generated Ad Text: %s", result_data["result"])
            break

        time.sleep(1)
