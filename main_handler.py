import logging
import time

import user_profile
from misc import dp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.ERROR)

logger = logging.getLogger(__name__)
start_time = time.time()


# decorator that logs all incoming updates
def msg_handler(function):
    def inside_decorator(update, context):
        logger.debug(str(update))
        return function(update, context)

    return inside_decorator


@dp.message_handler(commands=['start'], state="*")
async def start_handler(message, state):
    chat_id = message.chat.id
    if chat_id > 0:  # если это личный чат
        await user_profile.begin(message, state)
    else:
        await message.answer("Это групповой чат")


# log all errors
def error_handler(message, context):
    # logger.error('Error: {} ({} {}) caused.by {}'.format(context, type(context.error), context.error, update))
    print("Error: " + str(context.error))
    if message is not None:
        msg = "Error: {} {} for message {}".format(str(type(context.error))[:1000], str(context.error)[:2000],
                                                   str(message.text)[:1000])
        message.reply_text("Error")
    else:
        msg = "Error {} {} for ??? ({})".format(str(type(context.error))[:1000], str(context.error)[:1500],
                                                str(message)[:1500])
    print(msg)


