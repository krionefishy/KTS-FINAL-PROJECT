import typing
from app.FSM.state_accessor import FsmAccessor
from app.store.users.accessor import UserAccessor

if typing.TYPE_CHECKING:
    from app.bot.bot import Bot

async def process_command(bot: "Bot", message: dict):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    username = message["from"]["username"]
    command = message["text"].split()[0].lower()
    match command:
        case "/start":
            await process_command_start(bot, chat_id, user_id)
        case "/rules":
            await process_command_rules(bot, chat_id)
        case "/stop":
            await process_command_stop(bot, chat_id, user_id)
        case "/stats":
            await process_command_stats(bot, chat_id, user_id, username)

async def process_command_start(bot: "Bot", chat_id: int, user_id: int):
    fsm = FsmAccessor(bot.app)


    if await fsm.get_game_status(chat_id):
        await bot.send_message(chat_id, "Игра уже идет!")
        return
    
    await fsm.set_admin_id(chat_id, admin_id=user_id)

    game_handler = bot.get_game_handler()
    await game_handler.start_game(chat_id)

async def process_command_rules(bot: "Bot", chat_id):
    await bot.send_message(
        chat_id=chat_id,
        text="Правила"
    )


async def process_command_stop(bot: "Bot", chat_id: int, user_id: int):
    fsm = FsmAccessor(bot.app)

    if not await fsm.is_admin(chat_id, user_id):
        await bot.send_message(chat_id, "❌ Только администратор может остановить игру!")
        return
    
    game_handler = bot.get_game_handler()

    game_stats = await game_handler.stop_game(chat_id)

    message = "🛑 Игра остановлена администратором\n\n"
    if game_stats['players']:
        message += "🏆 Результаты:\n"
        for player in game_stats['players']:
            message += f"{player['username']}: {player['score']} очков\n"


    await bot.send_message(
        chat_id=chat_id,
        text=message,
    )

async def process_command_stats(bot: "Bot", chat_id: int, user_id: int, username: str):
    uac = UserAccessor(bot.app)

    user = await uac.get_stats(user_id=user_id)

    message = f'<a href="tg://user?id={user_id}">{username}</a>, вот ваша статистика!\n'
    message += f"🎮 Сыграно игр: {user.total_games}\n"
    message += f"🏆 Побед: {user.total_wins}\n"
    message += f"⭐ Всего очков: {user.total_score}\n"


    await bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode="HTML"
    )