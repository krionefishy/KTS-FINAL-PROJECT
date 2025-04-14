from app.bot.web.app import View
from app.bot.web.shemas import RespShema,ThemeRequestShemaPost
from aiohttp_apispec import response_schema, request_schema
from app.pkg.utils import json_responce


class ThemeView(View):
    @response_schema(RespShema, 200)
    @request_schema(ThemeRequestShemaPost)
    async def post(self):
        data = self.request.json()

        title = data["theme"]

        await self.request.app.store.theme.create_theme(title)
        
        return json_responce(data = {"theme": title})
    

