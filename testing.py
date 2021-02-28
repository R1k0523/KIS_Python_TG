import importlib
import json
from pathlib import Path

def func_info(func_name, args, predicted_answer, got_answer):
    return f'Имя функции: {func_name}||' \
           f'Аргументы: {args}||' \
           f'Ожидаемый результат: {predicted_answer}||' \
           f'Полученный результат: {got_answer}||'

def testing(group, student_num, file_name):
    tasks = json.loads(Path('tasks.json').read_text(encoding='utf-8'))
    students_file = importlib.import_module(f'documents.{file_name}')
    errors = []
    for ind, task in enumerate(tasks['tasks_list']):
        tests = importlib.import_module(f'tests.{task["folder_name"]}.{group}').tests
        for func_num in range(task['count']):
            func_name = f'{tasks["letter"]}{ind + 1}{func_num + 1}'
            func_tests = tests[func_name][student_num - 1]
            tested_func = getattr(students_file, func_name)
            for test in func_tests:
                # оно не работает, так как у тестов проблемы с точностью
                if ind > 0:
                    res = tested_func(test[0])
                else:
                    res = tested_func(*test[0])
                if type(res) == float:
                    try:
                        assert round(res, 10) == round(test[1], 10), func_info(func_name, test[0], test[1], res)
                    except Exception as e:
                        errors.append(e)
                else:
                    try:
                        assert res == test[1], func_info(func_name, test[0], test[1], res)
                    except Exception as e:
                        errors.append(e)

    return errors


print(testing('К6', 16, 'file_1'))
