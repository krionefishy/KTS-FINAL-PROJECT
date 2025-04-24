from aiohttp.web_exceptions import HTTPNotFound
from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.store.database.modles import Answer, AnswerModel


class AnswerAccessor(BaseAccessor):
    async def get_answers(self, question_id: int) -> Answer:
        async with self.app.database.session() as session:
            result = await session.execute(select(AnswerModel.answers).where(AnswerModel.id == question_id))

            answer = result.scalar_one_or_none()
            if answer is None:
                raise HTTPNotFound(text="answers does not exists for this question", content_type="application/json")

            return Answer(question_id=question_id, answers=answer)

    async def check_answer(self, question_id: int, chosen_answer: str) -> bool:
        try:
            answer_model = await self.get_answers(question_id)
            if not answer_model or not answer_model.answers:
                self.logger.error(f"No answers found for question {question_id}")
                return False

            for answer_dict in answer_model.answers:
                answer_text = next(iter(answer_dict))
                if answer_text == chosen_answer:
                    return answer_dict[answer_text]

            self.logger.error(f"Answer '{chosen_answer}' not found in options")
            return False

        except Exception as e:
            self.logger.error(f"Error checking answer: {e}")
            return False

    async def create_answer(self, question_id: int, answers: dict):
        # TODO Допилить
        raise NotImplementedError
