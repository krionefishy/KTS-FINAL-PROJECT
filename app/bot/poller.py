import asyncio
import typing

import aiohttp

if typing.TYPE_CHECKING:
    from app.bot.bot import Bot


class Poller:
    def __init__(self, bot: "Bot", session: aiohttp.ClientSession, poll_timeout: int = 30):
        self.bot = bot
        self.session = session
        self.timeout = int(poll_timeout)
        self.is_running = False
        self.base_url = f"https://api.telegram.org/bot{bot.token}/"
        self.offset = None
        self.logger = bot.app.logger.getChild("poller")
        self.dispatch_update = None

    async def setup_dispatch_update(self):
        from app.bot.handlers import dispatch_update

        self.dispatch_update = dispatch_update

    async def start(self):
        if self.is_running:
            return

        await self.setup_dispatch_update()

        self.is_running = True
        self.logger.info("Poller started")
        while self.is_running:
            try:
                updates = await self._get_updates()
                if updates:
                    for update in updates:
                        if "update_id" in update:
                            await self.dispatch_update(self.bot, update)
                            self.offset = update["update_id"] + 1
                        else:
                            self.logger.warning("Update without update_id: %s", update)
            except Exception as e:
                self.logger.error(f"Polling error {e}")
                await asyncio.sleep(5)

    async def stop(self):
        self.is_running = False
        self.logger.info("Poller stopped")
        await self.session.close()

    async def _get_updates(self) -> list[dict] | None:
        url = f"{self.base_url}getUpdates"

        params = {"timeout": self.timeout, "allowed_updates": ["message", "callback_query"]}
        if self.offset is not None:
            params["offset"] = self.offset

        self.logger.debug(f"Request params: {params}")
        try:
            async with self.session.get(url, params=params) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    self.logger.error(f"API error {resp.status}: {error}")
                    return None

                data = await resp.json()
                self.logger.debug(f"API response: {data}")

                if not data.get("ok", False):
                    self.logger.error(f"API not ok: {data}")
                    return None

                return data.get("result", [])

        except aiohttp.ClientError as e:
            self.logger.error(f"HTTP error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)!r}")
        return None
