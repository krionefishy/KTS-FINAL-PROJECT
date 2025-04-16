import aiohttp
import typing
from logging import getLogger
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
        return f"https://api.telegram.org/bot{self.token}"
    
    async def start(self):
        self.poller = Poller(self, self.session)
        await self.poller.start()

    async def send_message(self, chat_id: int, text: str, reply_markup=None):
        url = f"{self.base_url}getUpdates"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": reply_markup
        }

        async with self.session.post(url, json = payload) as resp:
            return await resp.json()
        


