import asyncio
import re
from time import sleep
from sanic.log import logger
from saweibot.utils.type_helper import parse_int

from ..helper import MessageHelepr


async def get_point(*params, helper: MessageHelepr):

    wrapper = helper.behavior_wrapper()
    _model = await wrapper.get(helper.user_id)
    temp = await helper.msg.reply(f"Point: {_model.msg_count}")
    logger.info(f"User [{helper.user.full_name}] query point: {_model.msg_count}")
    await asyncio.sleep(3)

    await asyncio.gather(
        temp.delete(),
        helper.msg.delete()
    )