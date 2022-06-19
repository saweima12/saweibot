from typing import List

import orjson
from saweibot.common.wrapper import BaseModelWrapper
from saweibot.common.redis import RedisHashMap

from ..entities import ChatWatchUser
from ..models import ChatWatchUserModel

class ChatWatcherUserWrapper(BaseModelWrapper[RedisHashMap]):
    
    def __init__(self, bot_id: str, chat_id: str):
        self.bot_id = bot_id
        self.chat_id = chat_id

    def _proxy(self):
        return self.factory(self.bot_id).get_hash_map(self.chat_id, "watch_user")

    async def exists(self, msg_id: str):
        return await self.proxy.exists_key(msg_id)

    async def get(self, user_id: str):
        result = await self.proxy.get(user_id)
        if result:
            _data = ChatWatchUserModel.parse_raw(result)
            return _data

        result = await ChatWatchUser.get_or_none(chat_id=self.chat_id, user_id=user_id)
        if result:
            return ChatWatchUserModel(**result.attach_json)

        return ChatWatchUserModel(user_id=user_id)


    async def set(self, user_id: str, data: ChatWatchUserModel):
        await self.proxy.set_key(user_id, data.json())


    async def save_db(self, user_id: str, data: ChatWatchUserModel, **kwargs):
        print(user_id, data)
        await ChatWatchUser.update_or_create({
            "attach_json": data.dict()
        }, chat_id=self.chat_id, user_id=user_id)

    async def save_all_db(self):
        result = await self.proxy.getall()

        for uid, attach in result.items():
            _uid = uid.decode()
            await ChatWatchUser.update_or_create({
                'attach_json': attach
            }, chat_id=self.chat_id, user_id=_uid)