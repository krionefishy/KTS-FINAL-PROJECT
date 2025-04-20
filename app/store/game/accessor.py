from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.base.base_accessor import BaseAccessor
from app.store.database.modles import ChatSession, Theme, ThemeModel, UserModel


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
                        current_game_state={
                                            'state': 'waiting_players',
                                            'current_player': None,
                                            'current_question': None,
                                            },
                        players={"players": []}
                    )
                )
                await session.commit()
                return 0
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error while starting game chat:{chat_id}, error: {e}")

    async def join(self, chat_id, user_id):
        try:
            async with self.app.database.session() as session:
                result = await session.execute(
                    select(ChatSession.players)
                    .where(ChatSession.chat_id == chat_id)
                ) 

                players_dict: dict[str, list[dict[int, int]]] = result.scalar_one_or_none()
                if not players_dict:
                    players_dict = {
                        "players": [
                            {user_id: 0}
                        ]
                    }
                    

                else:
                    players_dict["players"].append(
                        {user_id: 0}
                    )

                await session.execute(
                        update(ChatSession)
                        .where(ChatSession.chat_id == chat_id)
                        .values(
                            players=players_dict
                        )
                    )

                await session.commit()
                
        except Exception as e:
            await session.rollback()
            self.logger(f"Error while joining game chat_id: {chat_id}, error: {e}")

    async def write_current_theme(self, chat_id: int, theme_id: int):
        try:
            async with self.app.database.session() as session:
                await session.execute(
                    update(ChatSession)
                    .where(ChatSession.chat_id == chat_id)
                    .values(
                        current_theme=theme_id
                    )
                )

                await session.commit()

        except Exception as e:
            await session.rollback()
            self.logger(f"Error while changing theme in chat: {chat_id}, error {e}")
            
    async def get_current_theme(self, chat_id: int) -> Theme:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(ChatSession.current_theme)
                .where(ChatSession.chat_id == chat_id)
            )

            theme_id = result.scalar_one_or_none()
            if not theme_id:
                return None 
            
            theme_title = await session.execute(
                select(ThemeModel.theme_name)
                .where(ThemeModel._id == theme_id)
                )
            
            title = theme_title.scalar_one_or_none()
            if not title:
                return None
            
            return Theme(
                id=theme_id,
                theme_name=title
            )
        
    async def write_score_stat(self, chat_id: int, user_id: int, price: int):
        try:
            async with self.app.database.session() as session:
                players = await session.execute(
                    select(ChatSession.players)
                    .where(ChatSession.chat_id == chat_id)
                )

                players_dict: dict[str, list[dict[int, int]]] = players.scalar_one_or_none()

                if players_dict is None:
                    return
                
                for player in players_dict["players"]:
                    if user_id in player:
                        player[user_id] += price

                stmt = (update(ChatSession)
                        .where(ChatSession.chat_id == chat_id)
                        .values(players=players_dict))
                await session.execute(stmt)

                exists = await session.execute(
                    select(UserModel).where(UserModel._id == user_id)
                )

                user = exists.scalar_one_or_none()
                if user:
                    new_ts = user.total_score + price
                    update_user_stmt = (
                        update(UserModel)
                        .where(UserModel._id == user_id)
                        .values(total_score=new_ts)
                    )
                    await session.execute(update_user_stmt)
                else:
                    insert_user_stmt = (
                        insert(UserModel)
                        .values(_id=user_id,
                                total_score=price,
                                total_games=1,
                                total_wins=0)
                    )
                    await session.execute(insert_user_stmt)

                await session.commit()

        except Exception as e:
            await session.rollback()
            self.logger.error(f"Error while writing score statistics {e}") 


    async def add_win_to_user_statistic(self, user_id: int):
        try:
            async with self.app.database.session() as session:
                user = await session.execute(
                    select(UserModel)
                    .where(UserModel._id == user_id)
                )

                user = user.scalar_one_or_none()
                if user:
                    stmt = (update(UserModel)
                            .where(UserModel._id == user_id)
                            .values(
                                total_games = user.total_games + 1,
                                total_wins = user.total_wins + 1
                            ))
                    
                    await session.execute(stmt)
                    await session.commit()

        except Exception as e:
            await session.rollback()
            self.logger.error(f"error while adding win stat {e}")


    async def add_total_games_stat(self, user_id: int):
        try:
            async with self.app.database.session() as session:
                stmt = (update(UserModel)
                        .where(UserModel._id == user_id)
                        .values(
                            total_games = UserModel.total_games + 1
                        ))

                
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            await session.rollback()
            self.logger(f"error incrementing counter {e}")


