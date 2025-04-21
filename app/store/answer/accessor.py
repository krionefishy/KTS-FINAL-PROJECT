from aiohttp.web_exceptions import HTTPNotFound
from sqlalchemy import select

from app.base.base_accessor import BaseAccessor
from app.store.database.modles import Answer, AnswerModel


class AnswerAccessor(BaseAccessor):
    async def get_answers(self, question_id: int) -> Answer:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(AnswerModel.answers)
                .where(AnswerModel.id == question_id)
            )

            answer = result.scalar_one_or_none()
            if answer is None:
                raise HTTPNotFound(
                    text="answers does not exists for this question",
                    content_type="application/json"
                )
            
            return Answer(question_id=question_id,
                          answers=answer)
        
    async def check_answer(self, question_id: int, chosen_answer: str) -> bool:
        as_model = await self.get_answers(question_id)

        options = as_model.answers

        if isinstance(options, dict):
            if chosen_answer in options:
                is_correct = options.get(chosen_answer, False)
                return bool(is_correct)
            self.logger.error("recieved answer is not in answers dictionay")
        else:
            self.logger.error("recieved object not a dictionary")

        return False
            
    async def create_answer(self, question_id: int, answers: dict):
        # TODO Допилить
        raise NotImplementedError
    
