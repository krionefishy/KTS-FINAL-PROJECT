from app.bot.bot import Bot
from app.bot.keyboards import create_join_kb


async def process_command(bot: "Bot", message: dict):
    chat_id = message["chat"]["id"]
    command = message["text"].split()[0].lower()

    if command == "/start":
        await bot.send_message(
            chat_id=chat_id,
            text="Привет, давайте поиграем, присоединяйтесь к игре по кнопке ниже",
            reply_markup=create_join_kb(chat_id)
        )

    