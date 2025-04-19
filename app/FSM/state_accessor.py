from app.base.base_accessor import BaseAccessor
from sqlalchemy import update, select
from sqlalchemy.dialects.postgresql import insert
from app.store.database.modles import ChatSession

class FsmAccessor(BaseAccessor):
    async def get_next_player(self, chat_id: int) -> int:
        try:
            async with self.app.database.session() as session:
                result = await session.execute(
                    select(ChatSession.players)
                    .where(ChatSession.chat_id == chat_id)
                )

                players_dict: dict[str, list[dict[int, int]]] = result.scalar_one_or_none()

                if players_dict:
                    next_player = players_dict["players"].pop(0)

                stmt = (update(ChatSession)
                        .where(ChatSession.chat_id == chat_id)
                        .values(
                            players = players_dict
                        ))
                await session.execute(stmt)
                await session.commit()

                for i in next_player.keys():
                    return i
        except Exception as e:
            await session.rollback()
            self.logger(f"error while getting next player {e}")



    async def add_last_player_to_queue(self, user_id: int, chat_id: int, user_score: int):
        try:
            async with self.app.database.session() as session:
                result = await session.execute(
                    select(ChatSession.players)
                    .where(ChatSession.chat_id == chat_id)
                )

                players_dict: dict[str, list[dict[int, int]]] = result.scalar_one_or_none()

                if players_dict:
                    players_dict["players"].append(
                        {
                            user_id: user_score
                        }
                    )  

                stmt = (update(ChatSession)
                        .where(ChatSession.chat_id == chat_id)
                        .values(
                            players = players_dict
                        ))
                
                session.execute(stmt)
                session.commit()

        except Exception as e:
            session.roollback
            self.logger.error(f"Error in adding to queue {e}")


    async def get_game_status(self, chat_id: int) -> bool:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(ChatSession.is_active)
                .where(ChatSession.chat_id == chat_id)
            )

            is_active = result.scalar_one_or_none()

            return bool(is_active)
        


    async def set_game_status(self, chat_id: int):
        try:
            async with self.app.database.session() as session:
                result = await session.execute(
                    select(ChatSession)
                    .where(ChatSession.chat_id == chat_id)
                )

                exists = result.scalar_one_or_none()

                if exists:
                    stmt = (update(ChatSession)
                            .where(ChatSession.chat_id == chat_id)
                            .values(is_active = True
                            ))
                    
                    session.execute(stmt)

                else:
                    stmt = (insert(ChatSession)
                            .values(chat_id=chat_id,
                                    is_active=True,
                                    players = {"players": []},
                                    current_game_state={
                                                        'state': 'waiting_players',
                                                        'current_player': None,
                                                        'question': None,
                                                        'message_id': None
                                                    }
                                    ))
                session.commit()

            
        except Exception as e:
            await session.rollback()
            self.logger.error(f"error setting game_status {e}")



    async def set_admin_id(self, chat_id: int, admin_id: int):
        try:
            async with self.app.database.session() as session:
                stmt = (update(ChatSession)
                        .where(ChatSession.chat_id == chat_id)
                        .values(
                            admin_id=admin_id
                        ))
                
                await session.execute(stmt)
                await session.commit()

        except Exception as e:
            await session.rollback()
            self.logger.error(f"error setting admin {e}")


    async def get_count_of_joined_players(self, chat_id: int) -> int:
        async with self.app.database.session() as session:
            players = await session.execute(
                select(ChatSession.players)
                .where(ChatSession.chat_id == chat_id)
            )


            players_dict = players.scalar_one_or_none()

            if players_dict:
                return len(players_dict["players"])
            
            else:
                return 0
            

    async def set_false_status(self, chat_id: int):
        try:
            async with self.app.database.session() as session:
                stmt = (update(ChatSession)
                        .where(ChatSession.chat_id == chat_id)
                        .values(
                            is_active=False
                        ))
                
                await session.execute(stmt)
                await session.commit()

        except Exception as e:
            await session.rollback()
            self.logger.error(f"Error while changing status {e}")
