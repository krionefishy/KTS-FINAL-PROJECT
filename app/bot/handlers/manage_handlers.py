from app.bot.bot import Bot
from app.bot.keyboards import create_join_kb, create_statistik_kb


async def process_command(bot: "Bot", message: dict):
    chat_id = message["chat"]["id"]
    command = message["text"].split()[0].lower()
    match command:
        case "/start":
            await process_command_start(bot, chat_id)
        case "/rules":
            await process_command_rules(bot, chat_id)
        case "/stop":
            await process_command_stop(bot, chat_id)


async def process_command_start(bot: "Bot", chat_id):
    await bot.send_message(
            chat_id=chat_id,
            text="Начинаем игру",
            reply_markup=create_join_kb(chat_id)
        )
    
    
async def process_command_rules(bot: "Bot", chat_id):
    await bot.send_message(
        chat_id=chat_id,
        text="Правила"
    )


async def process_command_stop(bot: "Bot", chat_id):
    # TODO добавить логику окончания игры
    await bot.send_message(
        chat_id=chat_id,
        text="Игра остановлена",
        reply_markup=create_statistik_kb(chat_id)
    )