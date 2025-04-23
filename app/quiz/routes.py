import typing

from app.quiz.question_view import QuestionAddView, QuestionGetView
from app.quiz.theme_view import ThemeAddView, ThemeListView

if typing.TYPE_CHECKING:
    from app.bot.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/quiz.add_theme", ThemeAddView)
    app.router.add_view("/quiz.list_themes", ThemeListView)
    app.router.add_view("/quiz.add_question", QuestionAddView)
    app.router.add_view("/question.get_question", QuestionGetView)
