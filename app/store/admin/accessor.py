import typing

if typing.TYPE_CHECKING:
    from app.bot.web.app import Application

import bcrypt
from aiohttp.web_exceptions import HTTPConflict
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from app.base.base_accessor import BaseAccessor
from app.store.database.modles import Admin, AdminModel, ChatSession


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        admin_from_config = app.config.admin

        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(admin_from_config.password.encode("utf-8"), 
                                  salt).decode("utf-8")

        async with self.app.database.session() as session:
            try:
                stmt = insert(AdminModel).values(
                    email=admin_from_config.email,
                    password=hashed_pw
                )

                stmt = stmt.on_conflict_do_nothing(index_elements=['email'])

                await session.execute(stmt)
                await session.commit()

            except Exception as e:
                await session.rollback()
                self.logger(f"error while creating admin on startup {e}")
                raise 

    async def get_active_sessions(self):

        async with self.app.database.session() as session:
            result = await session.execute(
                select(ChatSession.chat_id).where(ChatSession.is_active is True)
            )
            
            return result.scalars().all()

    async def create_admin(self, email: str, password: str) -> Admin:
        async with self.app.database.session() as session:
            try:
                salt = bcrypt.gensalt()
                hashed_pw = bcrypt.hashpw(
                    password.encode("utf-8"), salt
                ).decode("utf-8")
                
                result = await session.execute(
                    insert(AdminModel)
                    .values(email=email, password=hashed_pw)
                    .returning(AdminModel)
                )
                await session.commit()
                admin = result.scalar_one()
                return Admin(
                    id=admin.id,
                    email=admin.email,
                    password=admin.password
                )
            except IntegrityError:
                await session.rollback()
                raise HTTPConflict(reason="admin already exists")
            
    async def get_admin_by_email(self, email: str) -> Admin:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(AdminModel).where(AdminModel.email == email)
            )

            current_admin = result.scalar_one_or_none()
            if current_admin is None:
                return None
            
            return Admin(
                id=current_admin.id,
                email=current_admin.email,
                password=current_admin.password
            )
    