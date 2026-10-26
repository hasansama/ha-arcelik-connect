"""Private COSA cloud protocol as observed in the Arçelik Connect APK."""
from __future__ import annotations

import asyncio
import aiohttp

from homeassistant.exceptions import HomeAssistantError
from .const import API_ROOT, PROVIDER


class CosaApi:
    def __init__(self, session: aiohttp.ClientSession, email: str, password: str):
        self.session = session
        self.email = email
        self.password = password
        self.token: str | None = None
        self._login_lock = asyncio.Lock()

    async def _post(self, path: str, payload: dict, *, authenticated: bool = True) -> dict:
        if authenticated and not self.token:
            await self.login()
        for attempt in range(2):
            headers = {"provider": PROVIDER, "Content-Type": "application/json"}
            if authenticated:
                headers["authToken"] = self.token or ""
            try:
                async with asyncio.timeout(20):
                    async with self.session.post(API_ROOT + path, json=payload, headers=headers) as response:
                        response.raise_for_status()
                        data = await response.json(content_type=None)
            except (aiohttp.ClientError, TimeoutError, ValueError) as exc:
                raise HomeAssistantError("COSA sunucusuna erişilemiyor") from exc
            if not isinstance(data, dict):
                raise HomeAssistantError("COSA beklenmeyen yanıt döndürdü")
            if data.get("ok") == 1:
                return data
            if authenticated and attempt == 0:
                self.token = None
                await self.login()
                continue
            raise HomeAssistantError(f"COSA işlemi reddetti (kod: {data.get('code')})")
        raise HomeAssistantError("COSA isteği başarısız")

    async def login(self):
        async with self._login_lock:
            if self.token:
                return
            data = await self._post("/users/login", {"email": self.email, "password": self.password}, authenticated=False)
            token = data.get("authToken")
            if not token:
                raise HomeAssistantError("Giriş yanıtında token bulunamadı")
            self.token = token

    async def devices(self) -> list[dict]:
        return (await self._post("/endpoints/getEndpoints", {})).get("endpoints", [])

    async def status(self, device_id: str) -> dict:
        response = await self._post("/endpoints/getEndpoint", {"endpoint": device_id})
        endpoint = response.get("endpoint")
        if not isinstance(endpoint, dict):
            raise HomeAssistantError("Cihaz durumu bulunamadı")
        return endpoint

    async def command(self, device_id: str, kind: str, value: int | float):
        await self._post("/endpoints/sendACState", {"endpoint": device_id, "type": kind, "value": value})
