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
            markup.add(btn(f'{group["name"]}-{i+1}-{json_file["year"]}', f'groupnum_{i+1}'))
    else:
        for i in range(0, group['count'], 3):
            btn1 = btn(f'{group["name"]}-{i+1}-{json_file["year"]}', f'groupnum_{i+1}')
            if i < 24:
                btn2 = btn(f'{group["name"]}-{i+2}-{json_file["year"]}', f'groupnum_{i+2}')
                btn3 = btn(f'{group["name"]}-{i + 3}-{json_file["year"]}', f'groupnum_{i + 3}')
                markup.add(btn1, btn2, btn3)
            else:
                markup.add(btn1)
    return markup



def student_num_keyboard():
    markup = InlineKeyboardMarkup(row_width=5)
    for i in range(1, 40, 5):
        markup.add(btn(i, 'student_' + str(i)), btn(i + 1, 'student_' + str(i + 1)),
                   btn(i + 2, 'student_' + str(i + 2)), btn(i + 3, 'student_' + str(i + 3)), btn(i + 4, 'student_' + str(i + 4)))
    return markup


def yes_no_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(btn("Да", 'yes'), btn("Нет", 'no'))
    return markup



def info_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(btn("Направление", 'group_type'), btn("Номер группы", 'group_num'))
    markup.add(btn("Номер в списке", 'student_num'), btn("Выход", 'none'))
    return markup



def out_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(btn("Выход", 'out'))
    return markup
