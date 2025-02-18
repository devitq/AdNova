import logging
from http import HTTPStatus as status

from httpx import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_healthcheck(client: Client) -> None:
    response = client.get("/health?format=json")
    assert response.status_code == status.OK

    response_data = response.json()

    unhealthy_services = [
        service
        for service, status in response_data.items()
        if status != "working"
    ]

    for service in unhealthy_services:
        logger.error(
            "Service %s unhealthy: %s", service, response_data[service]
        )

    assert not unhealthy_services, (
        f"Some services are unhealthy: {', '.join(unhealthy_services)}"
    )
