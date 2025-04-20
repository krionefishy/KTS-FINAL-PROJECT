import typing
from aiohttp import ClientSession
from app.FSM.state_accessor import FsmAccessor
from app.bot.keyboards import create_join_kb
import asyncio

if typing.TYPE_CHECKING:
    from app.bot.bot import Bot
class GameHandler:
    def __init__(self, bot: "Bot", session: ClientSession):
        self.bot = bot
        self.session = session
        self.fsm = FsmAccessor(bot.app)

    async def connect(self):
        if hasattr(self, 'fsm') and hasattr(self.fsm, 'connect'):
            await self.fsm.connect()

    async def start_game(self, chat_id: int):
        is_active = await self.fsm.get_game_status(chat_id)

        if is_active:
            await self.bot.send_message(chat_id, "Игра уже идет")
            return 
        
        self.fsm.set_game_status(chat_id)


        message = await self.bot.send_message(
            chat_id=chat_id,
            text="Начинаем новую игру. Присоединяйстесь",
            reply_markup=create_join_kb(chat_id)
        )


        message_id = message["result"]["message_id"]

        asyncio.create_task(self._waiting_for_players(chat_id, message_id))


    async def stop_game(self, chat_id: int):
        players_list = await self.fsm.get_players_stat(chat_id=chat_id)

        await self.fsm.clear_game_session(chat_id)

        return players_list


    async def _waiting_for_players(self, chat_id: int, message_id: int):
        await asyncio.sleep(15)

        count_players = self.fsm.get_count_of_joined_players(chat_id)

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
            self.logger.error(f"Failed to delete message: {e}")

        await self._start_round(chat_id)



    async def handle_join(self, chat_id: int, user_id: int):
        await self.fsm.add_last_player_to_queue(user_id, chat_id, user_score=0)


    async def _delete_message(self, chat_id: int, message_id: int):
        await self.bot.delete_message(chat_id, message_id)



    async def _start_round(self, chat_id: int):
        await self.bot.send_message(
            chat_id=chat_id,
            text="Начинаем игру!"
        )

