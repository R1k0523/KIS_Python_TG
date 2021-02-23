from aiogram import executor
from misc import dp
import main_handler
if __name__ == '__main__':
    print("Started")
    executor.start_polling(dp, skip_updates=True)
