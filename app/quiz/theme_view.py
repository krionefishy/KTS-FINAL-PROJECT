from aiohttp.web_exceptions import HTTPConflict
from aiohttp_apispec import docs, request_schema, response_schema

from app.bot.web.app import View
from app.bot.web.shemas import ErrorResponse, ListThemeResponse, ThemeRequestShemaPost, ThemeResponse
from app.pkg.utils import error_json_response, json_response


class ThemeAddView(View):
    @docs(
        tags=["themes"],
        summary="Create theme",
        description="Create new quiz theme (Admin only)",
    )
    @response_schema(ThemeResponse, 201)
    @response_schema(ErrorResponse, 400)
    @response_schema(ErrorResponse, 401)
    @response_schema(ErrorResponse, 403)
    @response_schema(ErrorResponse, 409)
    @request_schema(ThemeRequestShemaPost)
    async def post(self):
        await self.check_authenticated()
        data = await self.request.json()
        title = data["theme"]

        try:
            theme = await self.request.app.store.theme.create_theme(title)
            return json_response(data={"id": theme.id, "theme_name": theme.theme_name}, status=201)

        except HTTPConflict as e:
            return error_json_response(http_status=409, status="conflict", message=str(e))


class ThemeListView(View):
    @docs(
        tags=["themes"],
        summary="List themes",
        description="Get list of all available themes (Admin only)",
    )
    @response_schema(ListThemeResponse, 200)
    @response_schema(ErrorResponse, 401)
    @response_schema(ErrorResponse, 403)
    async def get(self):
        await self.check_authenticated()
        themes = await self.request.app.store.theme.get_themes_for_game(count_themes=100)
        return json_response({"themes": [{"id": theme.id, "theme_name": theme.theme_name} for theme in themes]})
