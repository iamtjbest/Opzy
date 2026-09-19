import pytest
from httpx import AsyncClient

from tests.test_profile import auth_headers

URL = "/settings/notifications"


async def test_notification_settings_require_auth(client: AsyncClient):
    assert (await client.get(URL)).status_code == 401
    assert (await client.put(URL, json={"cadence": "weekly"})).status_code == 401


async def test_new_user_gets_the_defaults_without_a_profile(client: AsyncClient):
    headers = await auth_headers(client)

    resp = await client.get(URL, headers=headers)

    assert resp.status_code == 200
    assert resp.json() == {"cadence": "daily", "channel": "email"}


@pytest.mark.parametrize("cadence", ["instant", "daily", "weekly", "off"])
async def test_put_changes_the_cadence(client: AsyncClient, cadence: str):
    headers = await auth_headers(client)

    resp = await client.put(URL, json={"cadence": cadence}, headers=headers)

    assert resp.status_code == 200
    assert resp.json() == {"cadence": cadence, "channel": "email"}
    assert (await client.get(URL, headers=headers)).json()["cadence"] == cadence


@pytest.mark.parametrize(
    "body",
    [
        {"cadence": "monthly"},
        {},
        # The channel isn't settable: WhatsApp is deferred.
        {"cadence": "weekly", "channel": "whatsapp"},
    ],
)
async def test_put_rejects_bad_bodies(client: AsyncClient, body: dict):
    headers = await auth_headers(client)

    resp = await client.put(URL, json=body, headers=headers)

    assert resp.status_code == 422
    assert (await client.get(URL, headers=headers)).json()["cadence"] == "daily"


async def test_put_only_changes_the_callers_settings(client: AsyncClient):
    ada = await auth_headers(client, "ada@example.com")
    bola = await auth_headers(client, "bola@example.com")

    await client.put(URL, json={"cadence": "off"}, headers=ada)

    assert (await client.get(URL, headers=bola)).json()["cadence"] == "daily"
