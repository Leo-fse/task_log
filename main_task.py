"""各種タスクを実行するメインタスク

Usage:
  main_task.py [--task=<task-name> | --all-reset]
  main_task.py (-h | --help)

Options:
  -h --help     Show this screen.
  --reset       Reset all data.

"""
from datetime import datetime
from docopt import docopt
import pathlib
from colorama import Fore, Style
import settings
import shutil

import tasks.init_task as init_task
from tasks.gcode_main_info import gcode_main_info

RESULT_FILE_PATH = "./task_result.txt"


def _init():
    """
    プロセス管理の初期化を行う
    """
    fp = pathlib.Path(RESULT_FILE_PATH)
    fp.touch()


def _reset_all_data():
    """
    プロセス管理のファイルを削除し、タスクを全て再実行するようにする
    """
    print(f"Reset all data.")
    shutil.rmtree(settings.OUTPUT_DIR, ignore_errors=True)

    fp = pathlib.Path(RESULT_FILE_PATH)
    fp.unlink(missing_ok=True)


def _task_executor(task, *args):
    """
    指定タスクの関数を実行する。
    実行した際に例外が発生したら、その時点で終了する。
    完了したらプロセス管理ファイルに追記され、再度タスクを実行した際にはスキップされる
    Parameters
    -------------
    task: Function
    """
    task_name = task.__module__
    fp = pathlib.Path(RESULT_FILE_PATH)
    completed_tasks = fp.read_text().split('\n')

    if completed_tasks.count(task_name) > 0:
        print(
            f"{Fore.MAGENTA}{datetime.now()} [SKIP] {task_name} is completed.{Style.RESET_ALL}")
        return

    try:
        print(
            f"{Fore.GREEN}{datetime.now()} [EXEC] {task_name} is started.{Style.RESET_ALL}")
        task(*args)
    except Exception as e:
        print(
            f"{Fore.RED}{datetime.now()} [FAIL] {task_name} is failed.{Style.RESET_ALL}")
        print(e)
        exit()
    else:
        print(
            f"{Fore.CYAN}{datetime.now()} [SUCCESS] {task_name} is completed.{Style.RESET_ALL}")
        with fp.open(mode="a") as f:
            f.write(f"{task_name}\n")


def _force_task_executor(task, *args):
    try:
        print(
            f"{Fore.GREEN}{datetime.now()} [EXEC] {task_name} is started.{Style.RESET_ALL}")
        task(*args)
    except Exception as e:
        print(
            f"{Fore.RED}{datetime.now()} [FAIL] {task_name} is failed.{Style.RESET_ALL}")
        print(e)
        exit()
    else:
        print(
            f"{Fore.CYAN}{datetime.now()} [SUCCESS] {task_name} is completed.{Style.RESET_ALL}")


if __name__ == "__main__":
    arguments = docopt(__doc__)

    if arguments["--all-reset"]:
        _reset_all_data()

    if arguments["--task"]:
        task_name = arguments["--task"]
        _force_task_executor(
            locals()[f"{task_name}"].main)
        exit()
    _init()

    _task_executor(init_task.main)
    _task_executor(gcode_main_info.main)
