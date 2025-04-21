import logging
import typing

if typing.TYPE_CHECKING:
    from app.bot.bot import Bot

from . import game_handlers, manage_handlers


async def dispatch_update(bot: "Bot", update: dict):
    try:
        if "message" in update:
            message = update["message"]
            text = message.get("text", "").strip()
            if text.startswith("/"):
                await manage_handlers.process_command(bot, message)
        
        elif "callback_query" in update:
            game_handler = bot.get_game_handler()

            await game_handler.process_callback(bot, update["callback_query"])
    except Exception as e:
        logging.error(msg=f"Error in dispatch {e}")
        