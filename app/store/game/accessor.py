import random
from app.base.base_accessor import BaseAccessor
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from app.store.database.modles import ChatSession


class GameAccessor(BaseAccessor):
    async def start_game(self, chat_id: int, admin_id: int):
        async with self.app.database.session() as session:
            try:
                is_active_result = await session.execute(
                    select(ChatSession.is_active)
                    .where(ChatSession.chat_id == chat_id)
                )

                result = is_active_result.scalar_one_or_none()
                if result is None:
                    stmt = insert(ChatSession).values(
                        chat_id=chat_id,
                        is_active=True,
                        admin_id=admin_id,
                        players={},
                        current_game_state={}
                        )
                    await session.execute(stmt)
                    await session.commit()
                    return 0

                if result.is_active:
                    return 1


                await session.execute(
                    update(ChatSession)
                    .where(ChatSession.chat_id == chat_id)
                    .values(
                        is_active=True,
                        admin_id=admin_id,
                        current_game_state={},
                        players={}
                    )
                )
                await session.commit()
                return 0
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error while starting game chat: {chat_id}, error: {e}")

                
    async def join(self, chat_id, user_id):
        try:
            async with self.app.database.session() as session:
                result = await session.execute(
                    select(ChatSession.players)
                    .where(ChatSession.chat_id == chat_id)
                ) 

                players_dict = result.scalar_one_or_none()
                if not players_dict:
                    players_dict = {}
                    players_dict[chat_id] = {"points": 0}

                else:
                    players_dict[chat_id] = {"points": 0}


                await session.execute(
                        update(ChatSession)
                        .where(ChatSession.chat_id == chat_id)
                        .values(
                            players = players_dict
                        )
                    )

                await session.commit()
                

        except Exception as e:
            await session.rollback()
            self.logger(f"Error while joining game chat_id: {chat_id}, error: {e}")


    async def write_current_theme(self, chat_id: int, title: str):
        try:
            async with self.app.database.session() as session:
                await session.execute(
                    update(ChatSession)
                    .where(ChatSession.chat_id == chat_id)
                    .values(
                        current_theme = title
                    )
                )


                await session.commit()

        except Exception as e:
            await session.rollback()
            self.logger(f"Error while changing theme in chat: {chat_id}, error {e}")
            