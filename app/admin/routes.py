import typing


from app.admin.view import AdminLoginView, AdminCurrentView
if typing.TYPE_CHECKING:
    from app.bot.web.app import Application





def setup_routes(app: "Application"):
    app.router.add_view("/admin.login", AdminLoginView)
    app.router.add_view("/admin.current", AdminCurrentView)