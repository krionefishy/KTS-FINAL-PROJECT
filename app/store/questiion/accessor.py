import random

from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict
from sqlalchemy import insert, select

from app.base.base_accessor import BaseAccessor
from app.store.database.modles import Quesion, QuestionModel, ThemeModel


class QuizAccessor(BaseAccessor):
    async def get_question(
        self,
        question_theme_id: int,
        question_price: int
    ) -> Quesion:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(QuestionModel)
                .where(QuestionModel.theme_id == question_theme_id,
                       QuestionModel.price == question_price)
            )
            result = result.scalars().all()
            if result is None:
                return None
            
            question_model = random.choice(result)

            if question_model is not None:
                return Quesion(
                    id=question_model.question_id,
                    theme_id=question_model.theme_id,
                    price=question_model.price,
                    question_text=question_model.question_text
                )
        return None
    
    async def create_question(
        self,
        theme_name: str,
        question_text: str,
        questtion_price: int
    ) -> Quesion:
        async with self.app.database.session() as session:
            try:
                theme_result = await session.execute(
                    select(ThemeModel._id)
                    .where(ThemeModel.theme_name == theme_name)
                )

                theme_id = theme_result.scalar_one_or_none()
                if theme_id is None:
                    raise HTTPBadRequest(
                        text="Theme does not exists",
                        content_type="application/json"
                    )

                result = await session.execute(
                    select(QuestionModel)
                    .where(QuestionModel.theme_id == theme_id,
                        QuestionModel.question_text == question_text,
                        QuestionModel.price == questtion_price)
                )

                result = result.scalar_one_or_none()
                if result is not None:
                    raise HTTPConflict(
                        text=f"Question {question_text} already exists",
                        content_type="application/json"
                    )

                stmt = insert(QuestionModel).values(theme_id=theme_id)
                await session.execute(stmt)
                await session.commit()

                return Quesion(
                    id=result.question_id,
                    theme_id=result.theme_id,
                    price=result.price,
                    question_text=result.question_text
                )
            except HTTPBadRequest:
                raise
            
            except HTTPConflict:
                raise

            except Exception as e:
                await session.rollback()
                self.logger(f"error while adding question {e}")
                raise