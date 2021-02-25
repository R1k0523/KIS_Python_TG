import json
import os
import re

from aiogram.dispatcher.filters.state import StatesGroup, State

import mail_sender
from keyboards import *
from misc import bot, dp
from aiogram.dispatcher import FSMContext

def user_info_text(group_type, group_num, year, student_num):
    return f'Группа: {group_type}-{group_num}-{year}\n' \
           f'Номер в группе: {student_num}' \
           f'\n\nВсе ли верно?'

class Sending(StatesGroup):
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
    await state.update_data(group_type=None)
    await prepare_group_type(message)


async def prepare_group_type(message):
    await message.answer('Выбери направление', reply_markup=group_type_keyboard())
    await Sending.group_type.set()


async def prepare_group_num(message, group_type):
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer('Выбери номер группы', reply_markup=group_num_keyboard(group_type))
    await Sending.group_num.set()


async def prepare_student_num(message):
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer('Выбери номер в списке', reply_markup=student_num_keyboard())
    await Sending.student_num.set()


async def prepare_file(message):
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer('Прикрепите файл')
    await Sending.wait_file.set()


async def msg_out(message):
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer('Вы действительно хотите выйти?',
                         reply_markup=yes_no_keyboard())
    await Sending.try_to_out.set()




async def user_info(message, state):
    data = await state.get_data()

    json_file = json.loads(Path('groups.json').read_text(encoding='utf-8'))
    group = json_file['group_list'][int(data["group_type"])]
    await message.answer(user_info_text(group["name"], data["group_num"], json_file['year'], data["student"]),
                         reply_markup=yes_no_keyboard())


async def send_info(message, state):
    data = await state.get_data()

    json_file = json.loads(Path('groups.json').read_text(encoding='utf-8'))
    group = json_file['group_list'][int(data["group_type"])]
    subject = f'{group["name"][1]}{data["group_num"]} {data["student"]}'
    mail_sender.sendmsg(subject, data["file_name"])
    os.remove(f'documents/{data["file_name"]}')
    await message.answer('Файл успешно отправлен', reply_markup=send_more_keyboard())
    await Sending.exit.set()




@dp.callback_query_handler(lambda call: call.data.split('_')[0] == 'grouptype', state=Sending.group_type)
async def group_type_handler(call, state):
    async def is_group_num_okay(group_type):
        json_file = json.loads(Path('groups.json').read_text(encoding='utf-8'))
        group = json_file['group_list'][int(group_type)]
        group_num = int((await state.get_data())['group_num'])
        return not group['count'] or group_num <= group['count']
    message = call.message
    group_type = call.data.split('_')[1]
    await state.update_data(group_type=group_type)
    await state.update_data(step='group_type')
    is_second = (await state.get_data())['is_second']
    print(f'is_second: {is_second}')

    if is_second and (await is_group_num_okay(group_type)):
        await Sending.is_right.set()
        await user_info(message, state)
    else:
        await prepare_group_num(message, group_type)


@dp.callback_query_handler(lambda call: call.data.split('_')[0] == 'groupnum', state=Sending.group_num)
async def group_num_handler(call, state):
    message = call.message
    group_num = call.data.split('_')[1]
    await state.update_data(group_num=group_num)
    await state.update_data(step='group_num')
    is_second = (await state.get_data())['is_second']
    if is_second:
        await Sending.is_right.set()
        await user_info(message, state)
    else:
        await prepare_student_num(message)


@dp.callback_query_handler(lambda call: call.data.split('_')[0] == 'student', state=Sending.student_num)
async def student_num_handler(call, state):
    message = call.message
    student_num = call.data.split('_')[1]
    await state.update_data(student=student_num)
    await state.update_data(step='student_num')
    is_second = (await state.get_data())['is_second']
    if is_second:
        await Sending.is_right.set()
        await user_info(message, state)
    else:
        await state.update_data(is_second=True)
        await prepare_file(message)


@dp.callback_query_handler(lambda call: True, state=Sending.try_to_out)
async def confirm_exit_handler(call, state):
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


@dp.message_handler(content_types=['document'], state=Sending.wait_file)
async def file_handler(message, state):
    document = message.document
    if re.search(r'.py$', document['file_name']):
        file = (await bot.get_file(document.file_id))
        file_name = str((await file.download()).name).split('/')[1]
        await state.update_data(file_name=file_name)
        await Sending.is_right.set()
        await user_info(message, state)
    else:
        await message.answer('Расширение файла не ".py"')

#ПРОВЕРКА ИНФОРМАЦИИ

@dp.callback_query_handler(lambda call: True, state=Sending.is_right)
async def is_right_handler(call, state):
    message = call.message
    if call.data == 'yes':
        await send_info(message, state)
        await bot.delete_message(message.chat.id, message.message_id)
    elif call.data == 'no':
        await message.answer("Что нужно изменить?", reply_markup=info_keyboard())
        await Sending.whats_wrong.set()
        await bot.delete_message(message.chat.id, message.message_id)


@dp.callback_query_handler(lambda call: True, state=Sending.whats_wrong)
async def whats_wrong_handler(call, state):
    message = call.message
    if call.data == 'group_type':
        await prepare_group_type(message)
    elif call.data == 'group_num':
        group_type = (await state.get_data())['group_type']
        await prepare_group_num(message, group_type)
    elif call.data == 'student_num':
        await prepare_student_num(message)
    elif call.data == 'file':
        await prepare_file(message)
    elif call.data == 'none':
        await Sending.is_right.set()
        await user_info(message, state)
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

@dp.callback_query_handler(lambda call: call.data == 'send_more', state='*')
async def seng_more_handler(call, state):
    message = call.message
    print('keeeeek')
    await begin(message, state)
    await bot.delete_message(message.chat.id, message.message_id)