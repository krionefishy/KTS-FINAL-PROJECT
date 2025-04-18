from app.base.base_accessor import BaseAccessor

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from app.store.database.modles import Answer, AnswerModel
from aiohttp.web_exceptions import HTTPNotFound


class AnswerAccessor(BaseAccessor):
    async def get_answers(self, question_id: int):
        async with self.app.database.session() as session:
            result = await session.execute(
                select(AnswerModel.answers).where(AnswerModel.id == question_id)
            )

            answer = result.scalar_one_or_none()
            if answer is None:
                raise HTTPNotFound(
                    text=f"answers does not exists for this question",
                    content_type="application/json"
                )
            
            return Answer(questiond_id=question_id,
                          answers=answer)
        

