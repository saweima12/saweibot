import os
import ujson
from telebot import TeleBot
from telebot.types import Message, Update, ChatMember

from sanic import Sanic, Request, json, text
from tortoise.contrib.sanic import register_tortoise

from saweibot import config
import saweibot.bots as bots
import saweibot.views as views

# define sanic app
app = Sanic(__name__)
app.update_config(config)

# Loading configure.
env_config_path = os.environ.get("SAWEIBOT_CONFIG")
if env_config_path and os.path.exists(env_config_path):
    app.update_config(env_config_path)

@app.before_server_start
async def startup(app: Sanic, loop):
    print("startup")
    await bots.register_bots(app)

@app.before_server_stop
async def shutdown(app:Sanic, loop):
    print("shutdown")


# register database orm.
register_tortoise(app, db_url=app.config['PEON_DB_URI'], modules={"entities": ["saweibot.entities"]}, generate_schemas=False)

# register blueprint
app.blueprint(views.tgbot)
