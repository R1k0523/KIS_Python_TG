import importlib
import json
from pathlib import Path


class TestException(AssertionError):
    def __init__(self, info):
        self.info = info


def func_info(func_name, args, predicted_answer, got_answer):
    return f'Имя функции: {func_name}\n' \
           f'Аргументы: {args}\n' \
           f'Ожидаемый результат: {predicted_answer}\n' \
           f'Полученный результат: {got_answer}'


def testing(group, student_num, file_name, q):
    tasks = json.loads(Path('tasks.json').read_text(encoding='utf-8'))
    test_info = {}
    try:
        students_file = importlib.import_module(f'documents.{file_name}')
        for ind, task in enumerate(tasks['tasks_list']):
            tests = importlib.import_module(f'tests.{task["folder_name"]}.{group}').tests
            for func_num in range(task['count']):
                func_name = f'{tasks["letter"]}{ind + 1}{func_num + 1}'
                func_tests = tests[func_name][student_num - 1]
                try:
                    tested_func = getattr(students_file, func_name)
                    for test in func_tests:
                        if ind > 0:
                            res = tested_func(test[0])
                        else:
                            res = tested_func(*test[0])
                        if type(res) is float:
                            if '%.2e' % res != '%.2e' % test[1]:
                                raise TestException(func_info(func_name, test[0], test[1], res))
                        else:
                            if res != test[1]:
                                raise TestException(func_info(func_name, test[0], test[1], res))
                    test_info[func_name] = 'Тест пройден'
                except TestException as e:
                    test_info[func_name] = f'Тест не пройден\nПричина:\n{e.info}'
                except Exception as e:
                    test_info[func_name] = f'Тест не пройден\nПричина:\n{e}'
    except Exception as e:
        test_info['Перед тестированием'] = str(e)


    q.put(test_info)

