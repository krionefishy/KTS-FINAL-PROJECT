import typing
from logging import getLogger

import aiohttp

from app.bot.poller import Poller

if typing.TYPE_CHECKING:
    from app.bot.web.app import Application


class Bot:
    def __init__(self, token: str, app: "Application" = None):
        self.token = token
        self.session = aiohttp.ClientSession()
        self.poller = None
        self.app = app  
        self.logger = getLogger("bot")

    @property
    def base_url(self):
        return f"https://api.telegram.org/bot{self.token}/"
    
    async def start(self):
        self.poller = Poller(self, 
                             self.session,
                             poll_timeout=self.app.config.bot.poll_timeout if self.app else 30
                            )
        
        await self.poller.start()

    async def send_message(self, chat_id: int, text: str, reply_markup=None, parse_mode = "HTML"):
        url = f"{self.base_url}sendMessage"
        payload = {
            "chat_id": int(chat_id),
            "text": text,
             "parse_mode": parse_mode
        }

        if reply_markup:
            payload["reply_markup"] = reply_markup
        headers = {
        "Content-Type": "application/json"
        }
        async with self.session.post(url, json=payload, headers=headers) as resp:
            return await resp.json()
        
    async def close(self):
        if self.poller:
            await self.poller.stop()
        await self.session.close()

