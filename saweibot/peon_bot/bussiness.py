# coding=utf-8
from sanic.log import logger
from aiogram import Bot
from aiogram.types import Message, ChatPermissions

from saweibot.peon_bot.data.entities import PeonChatConfig

from .data.meta import SERVICE_CODE
from .data.wrappers.deleted_message import DeletedMessageWrapper
from .helper import MessageHelepr
from .command import map as command_map

async def process_start_command(message: Message):
    helper = MessageHelepr(SERVICE_CODE, message)

    # must be group.
    if not helper.is_group():
        return

    is_group_registered = await helper.is_group_registered()
    is_whitelist_user = await helper.is_whitelist_user()
    # check group is registered or user is whitelist user.
    if (not is_group_registered) and (not is_whitelist_user):
        return 

    is_group_admin = await helper.is_group_admin()
    if not is_group_admin and not is_whitelist_user:
        return

    # register group chat.
    wrapper = helper.chat_config_wrapper()
    # set module.
    config = await wrapper.get_model()
    config.status = "ok"
    # add to redis.
    await wrapper.save_proxy(config)


    # write to database
    _default = {'status': 'ok', 'config_json': config.dict()}
    await PeonChatConfig.update_or_create(_default,
                                        chat_id=helper.chat_id)
    await message.reply(f"Set bot active on {helper.chat.full_name} group.")
    logger.info(f"Set bot active on {helper.chat_id} group.")


async def process_stop_command(message: Message):
    helper = MessageHelepr(SERVICE_CODE, message)

    if not helper.is_group():
        return

    # set config to disable
    if not await helper.is_group_registered():
        return 

    # check user permission.
    in_whitelist = await helper.is_whitelist_user()
    is_group_admin = await helper.is_group_admin()

    if not in_whitelist and not is_group_admin:
        return
    
    # disable bot at taget gorup.
    wrapper = helper.chat_config_wrapper()
    await wrapper.proxy.set("ng", ".status")

    # write to database
    _update = { 'status': 'ng' }
    await PeonChatConfig.update_or_create(defaults=_update, chat_id=helper.chat_id)
    await message.reply(f"Set bot inactive on {helper.chat.full_name} group.")


async def process_join_chat(message: Message):
    # logger.info("on join:", message.as_json())
    print(message)
    helper = MessageHelepr(SERVICE_CODE, message)
    print(message.chat.type)
    # if not await helper.is_senior_member():
    #     return

    #  add restrict
    chat = helper.chat
    await chat.restrict(helper.user_id, 
                    can_send_messages=True,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False)
    # write into watch list.
    wrapper = helper.watcher_wrapper()
    model = await wrapper.get(helper.user_id)
    model.full_name = helper.user.full_name
    await wrapper.set(helper.user_id, model)



async def process_chat_message(message: Message):
    helper = MessageHelepr(SERVICE_CODE, message)
    
    if helper.is_group():
        await _process_group_msg(helper)

    elif helper.is_private_chat():
        await _process_private_msg(helper)

async def _process_group_msg(helper: MessageHelepr):
    logger.debug(helper.msg.as_json())

    # check chat_id in whitelist.
    if not await helper.is_group_registered() :
        return

    # custom command handle
    if helper.is_text():
        if command_map.is_avaliable(helper.content):
            await command_map.notify(helper.content, helper=helper)
            return

    # check file is ok.
    deleted_wrapper = helper.deleted_message_wrapper()
    message_wrapper = await helper.chat_message_wrapper()
    # check will overflow.
    if await message_wrapper.will_overflow():
        last = await message_wrapper.last()
        # if overflow, check deleted_list.
        if await deleted_wrapper.exists(last.message_id):
            await deleted_wrapper.delete(last.message_id)
            logger.info("delete expired message.")

    # write into msg buffer.
    await message_wrapper.append(helper.message_model)

    if not helper.is_text():
        return 

    # increase message counter
    behavior_wrapper = helper.behavior_wrapper()
    count = await behavior_wrapper.get(helper.user_id)  
    await behavior_wrapper.set(helper.user_id, count + 1)
    await behavior_wrapper.save_all_db()

async def _process_private_msg(helper: MessageHelepr):
    pass