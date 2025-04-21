from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.base.base_accessor import BaseAccessor
from app.store.database.modles import ChatSession, Theme


class FsmAccessor(BaseAccessor):
    async def get_next_player(self, chat_id: int) -> int:
        try:
            async with self.app.database.session() as session:
                result = await session.execute(
                    select(ChatSession.players)
                    .where(ChatSession.chat_id == chat_id)
                )

                players_dct: dict[str, list[dict[int, int]]] = result.scalar_one_or_none()

                if players_dct:
                    next_player = players_dct["players"].pop(0)
                    players_dct['players'].append(next_player)

                stmt = (update(ChatSession)
                        .where(ChatSession.chat_id == chat_id)
                        .values(
                            players=players_dct
                        ))
                await session.execute(stmt)
                await session.commit()

                for u_id in next_player.keys():
                    return u_id
        except Exception as e:
            await session.rollback()
            self.logger.error(f"error while getting next player {e}")

    async def add_last_player_to_queue(self, user_id: int, chat_id: int):
        try:
            async with self.app.database.session() as session:
                result = await session.execute(
                    select(ChatSession.players)
                    .where(ChatSession.chat_id == chat_id)
                    .with_for_update()
                )
                
                players_data = result.scalar_one_or_none() or {"players": []}
                
                
                if any(str(user_id) in player for player in players_data["players"]):
                    return False
                    
                
                new_player = {str(user_id): 0}  
                players_data["players"].append(new_player)
                
                stmt = (
                    update(ChatSession)
                    .where(ChatSession.chat_id == chat_id)
                    .values(players=players_data)
                )
                
                await session.execute(stmt)
                await session.commit()

        except Exception as e:
            await session.rollback()
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
                            .values(is_active=True)
                            )
                    

                else:
                    stmt = (insert(ChatSession)
                            .values(chat_id=chat_id,
                                    is_active=True,
                                    players={"players": []},
                                    current_game_state={
                                                        'state': 'waiting_players',
                                                        'current_player': None,
                                                        'current_question': None,
                                                    }
                                    ))
                await session.execute(stmt)

                await session.commit()

        except Exception as e:
            await session.rollback()
            self.logger.error(f"error setting game_status {e}")

    async def set_admin_id(self, chat_id: int, admin_id: int):
        try:
            async with self.app.database.session() as session:
            
                result = await session.execute(
                    select(ChatSession)
                    .where(ChatSession.chat_id == chat_id)
                )

                current_session = result.scalar_one_or_none()

                if not current_session:
                    stmt = (
                        insert(ChatSession)
                        .values(
                            chat_id=chat_id,
                            admin_id=admin_id,
                            is_active=True,
                            players={"players": []},
                            current_game_state={
                                "state": "waiting_for_players",
                                "current_player": None,
                                "current_question": None,
                            },
                            current_theme=None
                        )
                    )
                else:
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

    async def is_admin(self, chat_id: int, user_id: int) -> bool:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(ChatSession.admin_id)
                .where(ChatSession.chat_id == chat_id)
            )

            admin_id = result.scalar_one_or_none()
            return admin_id == user_id

    async def clear_game_session(self, chat_id: int): 
        try:
            async with self.app.database.session() as session:
                stmt = (
                    update(ChatSession)
                    .where(ChatSession.chat_id == chat_id)
                    .values(
                        is_active=False,
                        admin_id=None,
                        players={
                            "players": []
                        },
                        current_game_state=None,
                        used_theme_questions=[],
                        game_themes=[]
                    )
                )

                await session.execute(stmt)
                await session.commit()

        except Exception as e:
            await session.rollback()
            self.logger.error(f"error clearing session {e}")

    async def get_players_stat(self, chat_id: int):
        async with self.app.database.session() as session:
            result = await session.execute(
                select(ChatSession.players)
                .where(ChatSession.chat_id == chat_id)
            )

            players_dict = result.scalar_one_or_none()

            if players_dict:
                return players_dict["players"]
            
            return []

    async def set_current_theme(self, chat_id: int, theme_id: int):
        try:
            async with self.app.database.session() as session:
                stmt = (update(ChatSession)
                        .where(ChatSession.chat_id == chat_id)
                        .values(
                            current_theme=theme_id
                        ))
                
                await session.execute(stmt)
                await session.commit()

        except Exception as e:
            await session.rollback()
            self.logger.error(f"error setting current theme {e}")

    async def get_current_theme(self, chat_id: int):
        async with self.app.database.session() as session:
            result = await session.execute(
                select(ChatSession.current_theme)
                .where(ChatSession.chat_id == chat_id)
            )

            theme_id = result.scalar_one_or_none()

            if theme_id:
                return theme_id

            return -1
            
    async def change_game_state(self, chat_id: int, data: dict):
        try:
            async with self.app.database.session() as session:
                stmt = (update(ChatSession)
                        .where(ChatSession.chat_id == chat_id)
                        .values(
                            current_game_state=data
                        ))
                
                await session.execute(stmt)
                await session.commit()

        except Exception as e:
            await session.rollback()
            self.logger.error(f"Error changing game_state {e}")

    async def check_user_id(self, chat_id: int, user_id: int) -> bool:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(ChatSession.current_game_state)
                .where(ChatSession.chat_id == chat_id)
            )

            game_state = result.scalar_one_or_none()
            if not game_state:
                return False 
            
            return str(game_state["current_player"]) == str(user_id)

    async def get_themes_of_session(self, chat_id) -> list[Theme]:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(ChatSession.game_themes)
                .where(ChatSession.chat_id == chat_id)
            )

            themes: list[tuple[str, int]] = result.scalar_one_or_none()

            if themes:
                result_list = []
                for theme in themes:
                    result_list.append(
                        Theme(
                            id=theme[1],
                            theme_name=theme[0]
                        )
                    )
                return result_list
            
            return []

    async def set_themes_for_session(self, chat_id: int, themes: list[Theme]):
        try:
            async with self.app.database.session() as session:
                new_list = [(theme.theme_name, theme.id) for theme in themes]
                stmt = (update(ChatSession)
                        .where(ChatSession.chat_id == chat_id)
                        .values(
                            game_themes=new_list
                        ))
                
                await session.execute(stmt)
                await session.commit()

        except Exception as e:
            await session.rollback()
            self.logger.error(f"error setting session themes {e}")

    async def check_count_answered_questions(self, chat_id: int) -> bool:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(ChatSession.game_themes, 
                       ChatSession.used_theme_questions)
                .where(ChatSession.chat_id == chat_id)
            )

            data = result.first()
            
            if data:
                game_themes, used_questions = data 

                if not game_themes or not used_questions:
                    return False
                
                return len(used_questions) == len(game_themes) * 3
            return False
        

    async def check_if_joined(self, chat_id: int, user_id:int):
        async with self.app.database.session() as session:
            result = await session.execute(
                select(ChatSession.players)
                .where(ChatSession.chat_id == chat_id)
            )

            players_data = result.scalar_one_or_none()

            if not players_data or not isinstance(players_data.get("players"), list):
                return False

            return any(
                str(user_id) in player for player in players_data["players"]
            )
        

    async def get_players_list(self, chat_id: int):
        async with self.app.database.session() as session:
            result = await session.execute(
                select(ChatSession.players)
                .where(ChatSession.chat_id == chat_id)
            )

            players = result.scalar_one_or_none()
            if not players or "players" not in players:
                return []

            players_data = players["players"]
            
            players_list = []
            for player_dict in players_data:
                if player_dict and isinstance(player_dict, dict):

                    user_id = next(iter(player_dict.keys()), None)
                    
                    if user_id is not None:
                        players_list.append(int(user_id))
            
            return players_list