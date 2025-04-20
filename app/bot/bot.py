import typing
from logging import getLogger

import aiohttp

from app.bot.poller import Poller
from app.bot.handlers.game_handlers import GameHandler
if typing.TYPE_CHECKING:
    from app.bot.web.app import Application


class Bot:
    def __init__(self, token: str, app: "Application" = None):
        self.token = token
        self.session = aiohttp.ClientSession()
        self.poller = None
        self.app = app  
        self.logger = getLogger("bot")
        self._game_handler = GameHandler(self, self.session)

    @property
    def base_url(self):
        return f"https://api.telegram.org/bot{self.token}/"
    
    def get_game_handler(self) -> GameHandler:
        return self._game_handler
    

    async def connect(self):
        if hasattr(self, '_game_handler') and self._game_handler:
            if hasattr(self._game_handler, 'connect'):
                await self._game_handler.connect()


    async def start(self):
        self.poller = Poller(self, 
                             self.session,
                             poll_timeout=self.app.config.bot.poll_timeout
                            )
        
        await self.poller.start()

    async def send_message(self, 
                           chat_id: int, 
                           text: str, 
                           reply_markup=None, 
                           parse_mode="HTML"):
        
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
        try:

            async with self.session.post(url, json=payload, headers=headers) as resp:
                return await resp.json()
            
        except Exception as e:
            self.logger.error(f"error sending message {str(e)!r}")
    
    async def delete_message(self, 
                             chat_id: int, 
                             message_id: int,
                             parse_mode="HTML"):
        
        url = f"{self.base_url}deleteMessage"

        params = {
            "chat_id": chat_id,
            "message_id": message_id,
        }
        headers = {
        "Content-Type": "application/json"
        }

        try:
            async with self.session.post(url, json=params, headers=headers) as resp:
                return await resp.json()
            
        except Exception as e:
            self.logger.error(f"error deleting message tg api {str(e)!r}")

    async def close(self):
        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()
        if self._game_handler:
            await self._game_handler.close()
