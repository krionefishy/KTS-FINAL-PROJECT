import bcrypt
from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session

from app.bot.web.app import View
from app.bot.web.shemas import AdminRequestShema, RespShema
from app.pkg.utils import error_json_responce, json_responce


class AdminView(View):
    @response_schema(RespShema, 200)
    @request_schema(AdminRequestShema)
    async def post(self):
        data = await self.request.json()

        email = data["email"]
        password = data["password"]

        admin_from_db = await self.request.app.store.admins.get_admin_by_email(email)

        if admin_from_db is None:
            return error_json_responce(
                http_status=404,
                status="Not found",
                message="Admin with such email was not found",
                data={}
            )

        if not bcrypt.checkpw(password.encode(), admin_from_db.password.encode()):
            return error_json_responce(
                http_status=403,
                status="forbidden",
                message="invalid credentials"
            )

        session = await new_session(request=self.request)
        session["admin_id"] = admin_from_db.id
        session.max_age = self.request.app.config.session.lifetime

        return json_responce(
            data={"id": admin_from_db.id, "email": email}
        )
    