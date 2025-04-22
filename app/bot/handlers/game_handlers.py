import asyncio
import logging
import typing

from aiohttp import ClientSession

from app.bot.keyboards import (
    create_answers_kb,
    create_join_kb,
    create_question_kb,
    create_theme_kb,
)
from app.FSM.state_accessor import FsmAccessor
from app.store.database.modles import Answer, Question
from app.store.game.accessor import GameAccessor

if typing.TYPE_CHECKING:
    from app.bot.bot import Bot


class GameHandler:
    def __init__(self, bot: "Bot", session: ClientSession):
        self.bot = bot
        self.session = session
        self.fsm = FsmAccessor(bot.app)
        self.game = GameAccessor(bot.app)

    async def connect(self):
        if hasattr(self, 'fsm') and hasattr(self.fsm, 'connect'):
            await self.fsm.connect()

    async def start_game(self, chat_id: int):
        is_active = await self.fsm.get_game_status(chat_id)

        if is_active:
            await self.bot.send_message(chat_id, "Игра уже идет")
            return 
        
        await self.fsm.set_game_status(chat_id)

        message = await self.bot.send_message(
            chat_id=chat_id,
            text="Начинаем новую игру. Присоединяйстесь",
            reply_markup=create_join_kb()
        )

        message_id = message["result"]["message_id"]

        asyncio.create_task(self._waiting_for_players(chat_id, message_id))

    async def stop_game(self, chat_id: int):
        players_list = await self.fsm.get_players_stat(chat_id=chat_id)
        await self.fsm.clear_game_session(chat_id)
        
        if not players_list:
            return {}
        
        """for player in players_list:
            user_id = next(iter(player.keys()))
            await self.game.add_total_games_stat(user_id)"""
        
        winner_dict = max(players_list, key=lambda x: next(iter(x.values())))
        winner_id = next(iter(winner_dict))
        winner_score = winner_dict[winner_id]
        
        await self.game.add_win_to_user_statistic(winner_id)
        
        return {
            'winner_id': winner_id,
            'winner_score': winner_score,
            'all_players': players_list
        }


    async def _waiting_for_players(self, chat_id: int, message_id: int):
        await asyncio.sleep(15)

        if not await self.fsm.get_game_status(chat_id):
            return 
        

        count_players = await self.fsm.get_count_of_joined_players(chat_id)

        if count_players == 0:
            await self.bot.send_message(
                chat_id=chat_id,
                text="❌ Не удалось начать игру - нет участников."
            )

            await self.fsm.set_false_status(chat_id)
            return 
        
        try:
            await self._delete_message(chat_id, message_id)
        except Exception as e:
            self.bot.logger.error("Error deleting message {e}")

        await self._start_round(chat_id)
        

    async def _delete_message(self, chat_id: int, message_id: int):
        await self.bot.delete_message(chat_id, message_id)

    async def _start_round(self, chat_id: int):
        await self.bot.send_message(
            chat_id=chat_id,
            text="Начинаем игру!"
        )

        user_id = await self.fsm.get_next_player(chat_id)
        username = await self.fsm.get_username(chat_id, user_id)
        username = username if username else "Игрок"
        themes = await self.bot.app.store.theme.get_themes_for_game(3)
        await self.fsm.set_themes_for_session(chat_id, themes)
        state_data = {
            "state": "selecting_theme",
            "current_player": user_id,
            "current_question": None
        }
        await self.fsm.change_game_state(chat_id, state_data)
        reply_markup = create_theme_kb(themes)

        await self.bot.send_message(
            chat_id=chat_id,
            text=f'<a href="tg://user?id={user_id}">{username}</a>, выберите тему вопроса\n',
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

    async def handle_join_game(self, chat_id: int, user_id: int, callback_query: dict):
        try:
            is_already_joined = await self.fsm.check_if_joined(chat_id, user_id)
            if is_already_joined:
                await self.bot.answer_callback_query(
                    callback_query_id=callback_query["id"],
                    text="Вы уже присоединились к игре"
                )
                return 
            

            await self.bot.answer_callback_query(
                callback_query_id=callback_query["id"],
                text="Вы присоединились к игре"
            )
            
            if await self.fsm.get_game_status(chat_id):
                await self.fsm.add_last_player_to_queue(user_id, chat_id)
                await self.game.add_total_games_stat(user_id)
            else:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="Пока что нельзя подключиться"
                )
        except Exception as e:
            logging.error(f"error join game {e}")
            await self.bot.send_message(
                chat_id=chat_id,
                text="Ошибка подключения"
            )
            
    async def handle_theme_selection(self, 
                                     chat_id: int, 
                                     theme_id: int, 
                                     user_id: int, 
                                     callback_query: dict):
        is_correct_player = await self.fsm.check_user_id(chat_id, user_id)

        current_state = await self.fsm.get_game_state(chat_id)

        if current_state:
            if not current_state["state"] == "selecting_theme":
                return 
            
        if not is_correct_player:
            await self.bot.answer_callback_query(
                callback_query_id=callback_query["id"],
                text="Сейчас не ваша очередь выбора темы",
            )
            return

        await self.fsm.set_current_theme(chat_id, theme_id)
        state_data = {
            "state": "selecting_question",
            "current_player": user_id,
            "current_question": None
        }
        await self.fsm.change_game_state(chat_id, state_data)

        questions_list: list[int] = [100, 200, 300]
        
        username = await self.fsm.get_username(chat_id, user_id)
        username = username if username else "Игрок"
        await self.bot.send_message(
            chat_id=chat_id,
            text=f'<a href="tg://user?id={user_id}">{username}</a>, выберите стоимость вопроса:\n',
            reply_markup=create_question_kb(questions_list),
            parse_mode="HTML"
        )

    async def handle_question_price(self, 
                                    chat_id: int, 
                                    price: int, 
                                    user_id: int, 
                                    callback_query: dict):
        is_correct_player = await self.fsm.check_user_id(chat_id, user_id)

        current_state = await self.fsm.get_game_state(chat_id)

        if current_state:
            if not current_state["state"] == "selecting_question":
                return 
            
        if not is_correct_player:
            await self.bot.answer_callback_query(
                callback_query_id=callback_query["id"],
                text="Сейчас не ваша очередь для выбора вопроса",
            )
            return

        theme_id = await self.fsm.get_current_theme(chat_id)
        if theme_id > 0:
            question: Question = await self.bot.app.store.quesions.get_random_question_for_game(chat_id, theme_id, price)
            if question is None:
                
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=f"Вопрос за стоимость {price} в этой теме уже был выбран до этого.\nВыберите другой вопрос"
                )
                return 
            state_data = {
                    "state": "selecting_answer",
                    "current_player": user_id,
                    "current_question": question.id
                }
            await self.fsm.change_game_state(chat_id, state_data)
            username = await self.fsm.get_username(chat_id, user_id)
            username = username if username else "Игрок"
            message = f'<a href="tg://user?id={user_id}">{username}</a>, Выберите ответ на вопрос ниже:\n'
            message += question.question_text

            answer = await self.bot.app.store.answers.get_answers(question.id)
            reply_markup = create_answers_kb(answer)        

            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )

    async def handle_answer(self, 
                            chat_id: int, 
                            user_id: int, 
                            question_id: int, 
                            idx: int,
                            callback_query: dict):
        is_correct_player = await self.fsm.check_user_id(chat_id, user_id)

        current_state = await self.fsm.get_game_state(chat_id)

        if current_state:
            if not current_state["state"] == "selecting_answer":
                return 

        if not is_correct_player:
            await self.bot.answer_callback_query(
                callback_query_id=callback_query["id"],
                text="Сейчас не ваша очередь для ответа",
            )
            return

        chosen_answer = callback_query["message"]["reply_markup"]["inline_keyboard"][idx][0]["text"]

        is_correct = await self.bot.app.store.answers.check_answer(question_id, chosen_answer)

        if is_correct:
            points = await self.bot.app.store.quesions.get_question_price(question_id)
            await self.game.write_score_stat(chat_id, user_id, points)

            await self.bot.send_message(
                chat_id=chat_id,
                text=f"✅ Правильно! +{points} очков\n Правильный ответ: {chosen_answer}"
            )

            if await self._check_end(chat_id):

                game_stats: list[dict[int, int]] = await self.stop_game(chat_id)
                message = "🛑 Игра завершена\n"

                if game_stats:
                    

                    winner_dict = max(game_stats, key=lambda x: next(iter(x.values())))

                    winner_user_id = next(iter(winner_dict))  

                    winner_score = winner_dict[winner_user_id]

                    await self.game.add_win_to_user_statistic(winner_user_id)
                    username = await self.fsm.get_username(chat_id, winner_user_id)
                    username = username if username else "Игрок"
                    message += "🏆 Результаты:\n"
                    message += f'<a href="tg://user?id={winner_user_id}">{username}</a>, со счетом {winner_score}\n'
                    

                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="HTML"
                )
                return 

            await self._next_turn(chat_id)
        else:
            next_player_id = await self.fsm.get_next_player(chat_id)

            state_data = {
                "state": "selecting_answer",
                "current_player": next_player_id,
                "current_question": question_id
            }
            await self.fsm.change_game_state(chat_id, state_data)
            username = await self.fsm.get_username(chat_id, next_player_id)
            username = username if username else "Игрок"
            message = "❌ Неправильный ответ\n"
            message += f'<a href="tg://user?id={next_player_id}">{username}</a>, Ваша очередь отвечать\n'
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="HTML"
            )
            await self.bot.answer_callback_query(
                callback_query_id=callback_query["id"],
                text="❌ Неверный ответ! Ход передан следующему игроку"
                )
        return 

    async def _next_turn(self, chat_id: int):
        
        next_player_id = await self.fsm.get_next_player(chat_id)

        state_data = {
            "state": "selecting_theme",
            "current_player": next_player_id,
            "current_question": None
        }
        await self.fsm.change_game_state(chat_id, state_data)

        themes = await self.fsm.get_themes_of_session(chat_id)
        username = await self.fsm.get_username(chat_id, next_player_id)
        username = username if username else "Игрок"
        await self.bot.send_message(
                            chat_id=chat_id,
                            text=f'🎲 <a href="tg://user?id={next_player_id}">{username}</a>, выберите тему вопроса:',
                            reply_markup=create_theme_kb(themes),
                            parse_mode="HTML"
                        )

    async def _check_end(self, chat_id: int) -> bool:
        return await self.fsm.check_count_answered_questions(chat_id)
    
    async def process_callback(self, callback_query: dict):
        chat_id = callback_query["message"]["chat"]["id"]
        user_id = callback_query["from"]["id"]
        callback_data: str = callback_query.get("data", "")

        if not callback_data:
            return 

        action, *params = callback_data.split(":")

        match action:
            case "join_game":
                await self.handle_join_game(chat_id, 
                                            user_id,
                                            callback_query)

            case "theme":
                theme_id = int(params[0])
                await self.handle_theme_selection(chat_id, 
                                                  theme_id, 
                                                  user_id, 
                                                  callback_query)

            case "question":
                question_price = int(params[0])
                await self.handle_question_price(chat_id, 
                                                 question_price, 
                                                 user_id,
                                                 callback_query)

            case "answer":
                question_id = int(params[0])
                idx = int(params[1])
                await self.handle_answer(chat_id, 
                                         user_id, 
                                         question_id, 
                                         idx, 
                                         callback_query)

