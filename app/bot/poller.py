import asyncio
from typing import Any

import aiohttp

from app.bot.bot import Bot
from app.bot.handlers import dispatch_update


class Poller:
    def __init__(self, bot: Bot, session: aiohttp.ClientSession):
        self.bot = bot
        self.session = session
        self.is_running = False 
        self.timeout = 30
        self.base_url = f"https://api.telegram.org/bot{bot.token}/"
        self.offset = None
        self.logger = bot.app.logger.getChild("poller")

    async def start(self):
        self.is_running = True
        self.logger.info("Poller started")
        while self.is_running:
            try:
                updates = await self._get_updates()
                if updates:
                    for update in updates:
                        await dispatch_update(self.bot, update)
                        self.offset = update["update_id"] + 1
            except Exception as e:
                self.logger.error(f"Polling error {e}")
                await asyncio.sleep(5)

    async def stop(self):
        self.is_running = False 
        self.logger.info("Poller stopped")

    async def _get_updates(self) -> list[dict[str, Any]] | None:
        url = f"{self.base_url}getUpdates"
        params = {
            "timeout": self.timeout,
            "offset": self.offset,
            "allowed_updates": ["message", "callback_query"]
        }
        try:
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("result", [])
        except aiohttp.ClientError as e:
            self.logger.error(f"HTTP error: {e}")
            return None