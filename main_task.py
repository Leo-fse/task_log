import pathlib

RESULT_FILE_PATH = "./task_result.txt"

def _init():
    """
    プロセス管理の初期化を行う
    """
    fp = pathlib.Path(RESULT_FILE_PATH)
    fp.touch()

if __name__ == "__main__":

    _init()

