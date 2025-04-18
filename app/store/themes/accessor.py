import random
from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from app.base.base_accessor import BaseAccessor
from app.store.database.modles import Theme, ThemeModel


class ThemeAccessor(BaseAccessor):
    async def create_theme(self, theme) -> Theme:
        async with self.app.database.session() as session:
            try:
                stmt = await session.execute(
                    select(ThemeModel).where(ThemeModel.theme_name == theme)  
                )
                res = stmt.scalar_one_or_none()
                if res is not None:
                    raise HTTPConflict(
                        text=f"Theme with name {theme} already exists",
                        content_type="application/json"
                    )

                stmt = insert(ThemeModel).values(theme_name=theme)
                await session.execute(stmt)
                await session.commit()

                return Theme(
                    id=res._id,
                    theme_name=res.theme_name
                )

            except HTTPConflict:
                raise

            except Exception as e:
                await session.rollback()
                self.logger(f"error while adding theme {e}")
                raise 

    async def delete_theme(self, theme) -> Theme:
        async with self.app.database.session() as session:
            try:
                stmt = await session.execute(
                    select(ThemeModel).where(ThemeModel.theme_name == theme)
                )

                if stmt.scalar_one_or_none() is None:
                    raise HTTPBadRequest(
                        text="Theme with such name does not exists",
                        content_type="application/json"
                    )
                
                stmt = delete(ThemeModel).where(ThemeModel.theme_name == theme)

                await session.execute(stmt)
                await session.commit()

            except HTTPBadRequest:
                raise 

            except Exception as e:
                await session.rollback()
                self.logger(f"error while deleting theme from db {e}")
                raise 

    async def get_theme(self, title):
        async with self.app.database.session() as session:
            result = await session.execute(
                select(ThemeModel)
            )

            result = random.choice(result.scalar_one_or_none())
            if not result:
                return None
            
            return Theme(
                id=result._id,
                theme_name=result.theme_name
            )