import os
import traceback
from urllib.parse import urljoin

from sanic import Sanic
from sanic.log import logger

from aiogram import Bot, Dispatcher
from aiogram.types import Message, ContentTypes, ChatType

from saweibot.bussiness import bll
from saweibot.meta import SERVICE_CODE

DP_CODE = f"{SERVICE_CODE}_dp"

def get_bot() -> Bot:
    app = Sanic.get_app()
    return Bot(token=app.config.TGBOT_PEON_TOKEN)

def get_dp() -> Dispatcher:
    app = Sanic.get_app()
    return getattr(app.ctx, DP_CODE)

def setup(app: Sanic) -> Bot:
    bot = Bot(token=app.config.TGBOT_PEON_TOKEN)
    dp = Dispatcher(bot)
    
    # handle start command
    @dp.message_handler(commands=['start'])
    async def on_start_command(message: Message):
        try:
            await bll.process_start_command(message)
        except Exception as _e:
            logger.error(traceback.format_exc())

    # handle start command
    @dp.message_handler(commands=['stop'])
    async def on_stop_command(message: Message):
        try:
            await bll.process_stop_command(message)
        except Exception as _e:
            logger.error(traceback.format_exc())

    # handle chat message, include sticker, animation, video, voice, text.
    @dp.message_handler(content_types=ContentTypes.ANY)
    async def on_chat_message(message: Message):
        try:
            await bll.process_chat_message(message)
        except Exception as _e:
            logger.error(traceback.format_exc())

    # Attach dispatcher to ctx
    setattr(app.ctx, DP_CODE, dp)
    logger.info(f"Register Dispatcher: {DP_CODE}")
    return bot

def set_current(bot: Bot):
    Bot.set_current(bot)
    return bot

async def set_webhook(app: Sanic, bot: Bot):
    # register webhook uri.
    hook_route = os.path.join("/peon", app.config.TGBOT_PEON_TOKEN)
    webhook_uri = urljoin(app.config['DOMAIN_URL'], hook_route)
    await bot.set_webhook(webhook_uri)

async def dispose(app: Sanic):
    if hasattr(app.ctx, DP_CODE):
        dp: Dispatcher = getattr(app.ctx, DP_CODE)
        await dp.reset_webhook()
        logger.info(f"Close Dispatcher: {DP_CODE}")
