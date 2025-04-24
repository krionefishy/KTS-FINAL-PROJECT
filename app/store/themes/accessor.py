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
                stmt = await session.execute(select(ThemeModel).where(ThemeModel.theme_name == theme))
                res = stmt.scalar_one_or_none()
                if res is not None:
                    raise HTTPConflict(text=f"Theme with name {theme} already exists", content_type="application/json")

                stmt = insert(ThemeModel).values(theme_name=theme)
                await session.execute(stmt)
                await session.commit()

                return Theme(id=res._id, theme_name=res.theme_name)

            except HTTPConflict:
                raise

            except Exception as e:
                await session.rollback()
                self.logger(f"error while adding theme {e}")
                raise

    async def delete_theme(self, theme) -> Theme:
        async with self.app.database.session() as session:
            try:
                stmt = await session.execute(select(ThemeModel).where(ThemeModel.theme_name == theme))

                if stmt.scalar_one_or_none() is None:
                    raise HTTPBadRequest(text="Theme with such name does not exists", content_type="application/json")

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
            result = await session.execute(select(ThemeModel))

            result = random.choice(result.scalar_one_or_none())
            if not result:
                return None

            return Theme(id=result._id, theme_name=result.theme_name)

    async def get_themes_for_game(self, count_themes: int) -> list[Theme]:
        try:
            async with self.app.database.session() as session:
                result = await session.execute(select(ThemeModel))

                result = result.scalars().all()

                if not result:
                    self.logger.warning("No themes in db")
                    return []

                shuffled_themes: list[ThemeModel] = result.copy()
                random.shuffle(shuffled_themes)

                if count_themes < len(shuffled_themes):
                    return_list = []
                    for i in range(count_themes):
                        current = shuffled_themes[i]
                        return_list.append(Theme(id=current._id, theme_name=current.theme_name))
                    return return_list

                return shuffled_themes
        except Exception as e:
            self.logger.error(f"error while getting themes {e}")
            return []
