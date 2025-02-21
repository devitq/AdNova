import os
import subprocess
import time
from collections.abc import Generator

import httpx
import pytest
from dotenv import load_dotenv

load_dotenv()

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8080")


@pytest.fixture(scope="session", autouse=True)
def docker_compose() -> Generator[None]:
    # btw, this is just in case you've forgotten to shut down compose :)
    subprocess.run(
        executable="docker",
        args=[
            "docker",
            "compose",
            "down",
        ],
        check=True,
    )
    subprocess.run(
        executable="docker",
        args=[
            "docker",
            "compose",
            "--project-name",
            "adnova-testing",
            "up",
            "-d",
            "--build",
            "--force-recreate",
            "--remove-orphans",
        ],
        check=True,
    )
    time.sleep(5)

    yield

    subprocess.run(
        executable="docker",
        args=[
            "docker",
            "compose",
            "--project-name",
            "adnova-testing",
            "down",
            "-v",
        ],
        check=True,
    )


@pytest.fixture(scope="session")
def client() -> Generator[httpx.Client]:
    with httpx.Client(base_url=BACKEND_BASE_URL, timeout=10.0) as client:
        yield client


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    items.sort(key=lambda item: "test_health" not in item.nodeid)
