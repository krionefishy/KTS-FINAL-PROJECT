from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict
from aiohttp_apispec import docs, request_schema, response_schema

from app.bot.web.app import View
from app.bot.web.shemas import ErrorResponse, QuestionRequestShemaPost, QuestionResponse
from app.pkg.utils import error_json_response, json_response


class QuestionAddView(View):
    @docs(
        tags=["questions"],
        summary="Create question",
        description="Create new quiz question (Admin only)",
    )
    @response_schema(QuestionResponse, 201)
    @response_schema(ErrorResponse, 400)
    @response_schema(ErrorResponse, 401)
    @response_schema(ErrorResponse, 403)
    @response_schema(ErrorResponse, 409)
    @request_schema(QuestionRequestShemaPost)
    async def post(self):
        await self.check_authenticated()
        data = await self.request.json()

        question_theme = data["theme_name"]
        question_text = data["question_text"]
        question_price = data["question_price"]

        try:
            question = await self.request.app.store.questions.create_question(
                question_theme, question_text, question_price
            )

            return json_response(
                {
                    "id": question.id,
                    "theme_id": question.theme_id,
                    "price": question.price,
                    "question_text": question.question_text,
                },
                status=201,
            )

        except HTTPBadRequest as e:
            return error_json_response(http_status=400, status="bad_request", message=str(e))
        except HTTPConflict as e:
            return error_json_response(http_status=409, status="conflict", message=str(e))


class QuestionGetView(View):
    @docs(
        tags=["questions"],
        summary="Get question",
        description="Get question by parameters (Admin only)",
    )
    @response_schema(QuestionResponse, 200)
    @response_schema(ErrorResponse, 400)
    @response_schema(ErrorResponse, 401)
    @response_schema(ErrorResponse, 403)
    @response_schema(ErrorResponse, 404)
    async def get(self):
        await self.check_authenticated()
        theme_id = self.request.query.get("theme_id")
        price = self.request.query.get("price")

        if not theme_id or not price:
            return error_json_response(
                http_status=400, status="bad_request", message="Parameters theme_id and price are required"
            )

        try:
            question = await self.request.app.store.quesions.get_question(int(theme_id), int(price))

            if not question:
                return error_json_response(http_status=404, status="not_found", message="Question not found")

            return json_response(
                {
                    "id": question.id,
                    "theme_id": question.theme_id,
                    "price": question.price,
                    "question_text": question.question_text,
                }
            )

        except ValueError:
            return error_json_response(
                http_status=400, status="bad_request", message="Invalid theme_id or price format"
            )
