import typing

from app.users.views.user_view import UserView

if typing.TYPE_CHECKING:
    from app.bot.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/user.get_stat", UserView)