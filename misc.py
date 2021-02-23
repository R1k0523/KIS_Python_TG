from aiogram.contrib.fsm_storage.memory import MemoryStorage
import secret_token
from aiogram import Bot, Dispatcher

bot = Bot(token=secret_token.token)
dp = Dispatcher(bot, storage=MemoryStorage())
