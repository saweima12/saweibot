import re
from saweibot.utils.type_helper import parse_int

from ..helper import MessageHelepr


async def get_point(*params, helper: MessageHelepr):

    wrapper = helper.behavior_wrapper()
    _model = await wrapper.get(helper.user_id)
    await helper.msg.reply(f"Point: {_model.msg_count}")