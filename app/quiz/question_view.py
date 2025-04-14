from aiohttp_apispec import request_schema, response_schema
from app.bot.web.shemas import QuestionRequestShemaPost, RespShema
from app.bot.web.app import View
from app.pkg.utils import json_responce
class QuestionView(View):
    @response_schema(RespShema, 200)
    @request_schema(QuestionRequestShemaPost)
    async def post(self):
        data = self.request.json()


        question_theme = data["theme_name"]
        question_text = data["question_text"]
        quesstion_price = data["question_price"]


        current_question = await self.request.app.store.quesions.create_question(question_theme, question_text, quesstion_price)

        return json_responce(data={
            "theme_id": current_question.theme_id,
            "text": current_question.question_text,
            "price": current_question.price
        })
    


    async def get(self):
        raise NotImplementedError