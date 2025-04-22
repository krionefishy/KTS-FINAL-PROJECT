import bcrypt
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import new_session
from aiohttp.web_exceptions import HTTPNotFound

from app.bot.web.app import View
from app.bot.web.shemas import AdminRequestSchema, AdminResponseSchema, ErrorResponse
from app.pkg.utils import error_json_response, json_response


class AdminLoginView(View):
    @docs(
        tags=["admin"],
        summary="Admin login",
        description="Authenticate admin user",
    )
    @response_schema(AdminResponseSchema, 200)
    @response_schema(ErrorResponse, 403)
    @response_schema(ErrorResponse, 404)
    @request_schema(AdminRequestSchema)
    async def post(self):
        data = await self.request.json()

        email = data["email"]
        password = data["password"]

        try:
            admin_from_db = await self.request.app.store.admins.get_admin_by_email(email)

            if not bcrypt.checkpw(password.encode(), admin_from_db.password.encode()):
                return error_json_response(
                    http_status=403,
                    status="forbidden",
                    message="Invalid credentials"
                )

            session = await new_session(request=self.request)
            session["admin_id"] = admin_from_db.id
            session.max_age = self.request.app.config.session.lifetime

            return json_response(
                data={"id": admin_from_db.id, "email": email}
            )
            
        except HTTPNotFound:
            return error_json_response(
                http_status=404,
                status="not_found",
                message="Admin not found",
                data={}
            )


class AdminCurrentView(View):
    @docs(
        tags=["admin"],
        summary="Get current admin",
        description="Get information about authenticated admin",
    )
    @response_schema(AdminResponseSchema, 200)
    @response_schema(ErrorResponse, 401)
    @response_schema(ErrorResponse, 403)
    async def get(self):
        admin = await self.check_authenticated()
        return json_response(
            data={"id": admin.id, "email": admin.email}
        )