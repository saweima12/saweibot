import os
from telebot import TeleBot
from telebot.types import Message, Update, ChatMember

from sanic import Sanic, Request, json, text
from sanic.log import logger
from tortoise.contrib.sanic import register_tortoise

from saweibot import config, storages, services

# define sanic app
app = Sanic(__name__)
app.update_config(config)

# Loading configure.
env_config_path = os.environ.get("SAWEIBOT_CONFIG")
if env_config_path and os.path.exists(env_config_path):
    app.update_config(env_config_path)

orm_modules = {
    "core_entities": ["saweibot.core.entities"]
}

# register storages.
storages.register(app)

# register services.
services.register(app, orm_modules)

# register database orm.
register_tortoise(app, 
    db_url=app.config['POSTGRES_URI'], 
    modules=orm_modules, 
    generate_schemas=True
)