from aiohttp_apispec import docs, response_schema

from app.bot.web.app import View
from app.bot.web.shemas import ErrorResponse, UserStatsResponse
from app.pkg.utils import error_json_response, json_response


class UserView(View):
    @docs(
        tags=["users"],
        summary="Get user stats",
        description="Get user statistics (Admin only)",
    )
    @response_schema(UserStatsResponse, 200)
    @response_schema(ErrorResponse, 400)
    @response_schema(ErrorResponse, 401)
    @response_schema(ErrorResponse, 403)
    @response_schema(ErrorResponse, 404)
    async def get(self):
        await self.check_authenticated()
        try:
            user_id = int(self.request.query.get("user_id"))
            user = await self.request.app.store.users.get_user(user_id)

            if not user:
                return error_json_response(http_status=404, status="not_found", message="User not found")

            return json_response(
                {
                    "user_id": user.id,
                    "total_score": user.total_score,
                    "total_games": user.total_games,
                    "total_wins": user.total_wins,
                }
            )

        except (ValueError, TypeError):
            return error_json_response(http_status=400, status="bad_request", message="Invalid user_id format")
