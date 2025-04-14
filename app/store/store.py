import typing 

from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.bot.web.app import Application

class Store:
    def __init__(self, app: "Application"):
        from app.store.users.accessor import UserAccessor
        from app.store.admin.accessor import AdminAccessor
        from app.store.answer.accessor import AnswerAccessor
        from app.store.questiion.accessor import QuizAccessor
        from app.store.themes.accessor import ThemeAccessor


        self.admins = AdminAccessor(app)
        self.user = UserAccessor(app)
        self.theme = ThemeAccessor(app)
        self.quesions = QuizAccessor(app)
        self.answers = AnswerAccessor(app)

    
    async def connect(self):
        await self.admins.connect()

    
    async def disconnect(self):
        await self.admins.disconnect()


def setup_store(app: "Application") -> None:
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)