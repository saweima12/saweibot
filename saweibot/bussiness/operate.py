from aiogram import Bot
from aiogram.types.message import Message
from aiogram.types.chat_permissions import ChatPermissions

from saweibot.data.entities import ChatDeletedMessage

async def set_media_permission(bot: Bot, chat_id: str, user_id: str, is_open: bool) -> bool:

    if is_open:
        permission = ChatPermissions(can_send_messages=True,
                                    can_send_media_messages=True,
                                    can_send_other_messages=True,
                                    can_add_web_page_previews=True)
    else:
        permission = ChatPermissions(can_send_messages=True,
                            can_send_media_messages=False,
                            can_send_other_messages=False,
                            can_add_web_page_previews=False)

    result = await bot.restrict_chat_member(chat_id, user_id, permission)

    return result


async def record_deleted_message(chat_id: str, data: Message):
    
    content_type = "forward" if data.is_forward() else data.content_type

    _data = data.to_python()

    _data['full_name'] = data.from_user.full_name
    _data['content_type'] = data.content_type

    # write into database 
    await ChatDeletedMessage.create(chat_id=chat_id, 
                                content_type=content_type,
                                message_json=_data)
