import asyncio
import importlib
import json
import queue
from pathlib import Path
from kthread import KThread


class TestException(AssertionError):
    def __init__(self, info):
        self.info = info


def __func_info__(func_name, args, predicted_answer, got_answer):
    return f'Имя функции: {func_name}\n' \
           f'Аргументы:\n{args}\n' \
           f'Ожидаемый результат:\n{predicted_answer}\n' \
           f'Полученный результат:\n{got_answer}\n'


def __testing__(group, student_num, file_name, q):
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
                                raise TestException(__func_info__(func_name, test[0], test[1], res))
                        else:
                            if res != test[1]:
                                raise TestException(__func_info__(func_name, test[0], test[1], res))
                    test_info[func_name] = '🟢\nТест пройден'
                except TestException as e:
                    test_info[func_name] = f'🔴\nТест не пройден\nПричина:\n{e.info}'
                except AttributeError:
                    pass
                except Exception as e:
                    test_info[func_name] = f'🔴\nТест не пройден\nПричина:\n{e}'
    except Exception as e:
        test_info['Перед тестированием'] = str(e)
    q.put(test_info)


async def testing(group, student_num, file_name):
    q = queue.Queue()
    t = KThread(target=__testing__, args=(group, student_num, file_name, q))
    t.start()
    await asyncio.sleep(5)
    if t.is_alive():
        t.kill()
    return q.get()
