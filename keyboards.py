import json
from pathlib import Path

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def btn(name, callback):
    return InlineKeyboardButton(name, callback_data=callback)


def group_type_keyboard():
    groups = json.loads(Path('groups.json').read_text(encoding='utf-8'))
    markup = InlineKeyboardMarkup()
    for i, group in enumerate(groups['group_list']):
        markup.add(btn(group['name'], f'grouptype_{i}'))
    return markup


def group_num_keyboard(group_index):
    json_file = json.loads(Path('groups.json').read_text(encoding='utf-8'))
    markup = InlineKeyboardMarkup(row_width=5)
    group = json_file['group_list'][int(group_index)]
    if group['count'] < 11:
        for i in range(group['count']):
            markup.add(btn(f'{group["name"]}-{(i + 1):02d}-{json_file["year"]}', f'groupnum_{i + 1}'))
    else:
        for i in range(0, group['count'], 3):
            btn1 = btn(f'{group["name"]}-{(i + 1):02d}-{json_file["year"]}', f'groupnum_{i + 1}')
            if i < 24:
                btn2 = btn(f'{group["name"]}-{(i + 2):02d}-{json_file["year"]}', f'groupnum_{i + 2}')
                btn3 = btn(f'{group["name"]}-{(i + 3):02d}-{json_file["year"]}', f'groupnum_{i + 3}')
                markup.add(btn1, btn2, btn3)
            else:
                markup.add(btn1)
    return markup


def student_num_keyboard():
    markup = InlineKeyboardMarkup(row_width=5)
    for i in range(1, 40, 5):
        btns = (btn(j, f'student_{j}') for j in range(i, i + 5))
        markup.add(*btns)
    return markup


def yes_no_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(btn("Да", 'yes'), btn("Нет", 'no'))
    return markup


def yes_no_test_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(btn("Да", 'yes'), btn("Нет", 'no'))
    markup.add(btn("Тест (Бета-версия)", 'test'), btn("Выход", 'go_out'))
    return markup


def info_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(btn("Направление", 'group_type'), btn("Номер группы", 'group_num'))
    markup.add(btn("Номер в списке", 'student_num'), btn("Назад", 'none'))
    return markup


def out_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(btn("Выход", 'out'))
    return markup


def send_more_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(btn("Отправить еще", 'send_more'))
    return markup
