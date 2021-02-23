import json
import os
import re

from aiogram.dispatcher.filters.state import StatesGroup, State

import mail_sender
from keyboards import *
from misc import bot, dp
from aiogram.dispatcher import FSMContext


class BDay(StatesGroup):
    group_type = State()
    group_num = State()
    student_num = State()
    wait_file = State()
    is_right = State()
    whats_wrong = State()
    try_to_out = State()
    exit = State()


async def begin(message, state: FSMContext):
    await state.update_data(is_second=False)
    await prepare_group_type(message)


async def prepare_group_type(message):
    await message.answer('Выбери направление', reply_markup=group_type_keyboard())
    await BDay.group_type.set()


async def prepare_group_num(message, group_type):
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer('Выбери номер группы', reply_markup=group_num_keyboard(group_type))
    await BDay.group_num.set()


async def prepare_student_num(message):
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer('Выбери номер в списке', reply_markup=student_num_keyboard())
    await BDay.student_num.set()


async def prepare_file(message):
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer('Прикрепите файл')
    await BDay.wait_file.set()


async def msg_out(call):
    message = call.message
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer('Вы действительно хотите выйти? Осталось совсем чуть-чуть. '
                         'Если вы совершили ошибку на раннем этапе, ее еще можно будет исправить',
                         reply_markup=yes_no_keyboard())
    await BDay.try_to_out.set()


async def is_right_user_info(message, state):
    await state.update_data(from_id=message.from_user.id)
    await message.answer('\n\nВсе ли верно? \nПозднее ты не сможешь изменить эту информацию',
                         reply_markup=yes_no_keyboard())


async def user_info(message, state, file_name):
    data = await state.get_data()

    json_file = json.loads(Path('groups.json').read_text(encoding='utf-8'))
    group = json_file['group_list'][int(data["group_type"])]

    subject = f'{group["name"][1]}{data["group_num"]} {data["student"]}'
    mail_sender.sendmsg(subject, file_name)
    os.remove(f'documents/{file_name}')
    await message.answer('Файл успешно отправлен')




@dp.callback_query_handler(lambda call: call.data.split('_')[0] == 'grouptype', state=BDay.group_type)
async def group_type_handler(call, state):
    message = call.message
    group_type = call.data.split('_')[1]
    await state.update_data(group_type=group_type)
    await state.update_data(step='group_type')
    is_second = (await state.get_data())['is_second']
    if is_second:
        await BDay.is_right.set()
        await is_right_user_info(message, state)
    else:
        await prepare_group_num(message, group_type)


@dp.callback_query_handler(lambda call: call.data.split('_')[0] == 'groupnum', state=BDay.group_num)
async def group_num_handler(call, state):
    message = call.message
    group_num = call.data.split('_')[1]
    await state.update_data(group_num=group_num)
    await state.update_data(step='group_num')
    is_second = (await state.get_data())['is_second']
    if is_second:
        await BDay.is_right.set()
        await is_right_user_info(message, state)
    else:
        await prepare_student_num(message)


@dp.callback_query_handler(lambda call: call.data.split('_')[0] == 'student', state=BDay.student_num)
async def student_num_handler(call, state):
    message = call.message
    student_num = call.data.split('_')[1]
    await state.update_data(student=student_num)
    await state.update_data(step='student_num')
    is_second = (await state.get_data())['is_second']
    if is_second:
        await BDay.is_right.set()
        await is_right_user_info(message, state)
    else:
        await prepare_file(message)


@dp.callback_query_handler(lambda call: True, state=BDay.try_to_out)
async def confirm_exit_q_handler(call, state):
    message = call.message
    if call.data == 'yes':
        await bot.delete_message(message.chat.id, message.message_id)
        await message.answer('Готово')
    elif call.data == 'no':
        step = (await state.get_data())['step']
        if step == 'group_type':
            await prepare_group_type(message)
        if step == 'group_num':
            group_type = state.get_data()['group_type']
            await prepare_group_num(message, group_type)
        if step == 'student_num':
            await prepare_student_num(message)
        if step == 'file':
            await prepare_file(message)


@dp.message_handler(content_types=['document'], state=BDay.wait_file)
async def file_handler(message, state):
    document = message.document
    if re.search(r'.py$', document['file_name']):
        file = (await bot.get_file(document.file_id))
        print(file)
        file_name = str((await file.download()).name).split('/')[1]
        print(file_name)
        await user_info(message, state, file_name)
    else:
        await message.answer('Расширение файла не ".py"')

#ПРОВЕРКА ИНФОРМАЦИИ

@dp.callback_query_handler(lambda call: True, state=BDay.is_right)
async def is_right_q_handler(call, state):
    message = call.message
    if call.data == 'yes':
        await user_info(message, state)
        await bot.delete_message(message.chat.id, message.message_id)
    elif call.data == 'no':
        await message.answer("Что нужно изменить?", reply_markup=info_keyboard())
        await BDay.whats_wrong.set()
        await bot.delete_message(message.chat.id, message.message_id)


@dp.callback_query_handler(lambda call: True, state=BDay.whats_wrong)
async def whats_wrong_q_handler(call, state):
    message = call.message
    if call.data == 'group_type':
        await prepare_group_type(message)
    elif call.data == 'group_num':
        group_type = state.get_data()['group_type']
        await prepare_group_num(message, group_type)
    elif call.data == 'student_num':
        await prepare_student_num(message)
    elif call.data == 'file':
        await prepare_file(message)
    elif call.data == 'none':
        await user_info(message, state)
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
