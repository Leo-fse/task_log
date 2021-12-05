import inspect
import logging
from functools import wraps


class CustomFilter(logging.Filter):
    """logger用のユーザー定義フィルター"""

    def filter(self, record):
        """呼び出し元のファイル名、関数名、行番号が表示されるようにする関数
        これでフィルタリングしないとデコレーターを使用した関数(呼び出し元)に関する情報ではなく、
        log.pyの後述のlog関数を元にした情報が出力される

        Returns:
            True: 常にフィルターをパスする
        """

        record.real_filename = getattr(
            record, 'real_filename', record.filename)
        record.real_funcName = getattr(
            record, 'real_funcName', record.funcName)
        record.real_lineno = getattr(record, 'real_lineno', record.lineno)

        return True


def get_logger():
    """logging.Loggerの作成

    Returns:
        logger (logging.Logger): logging.Loggerのインスタンス
    """

    log_format = '[%(asctime)s] %(levelname)s -> %(message)s\t%(real_filename)s' \
                 ' - %(real_funcName)s:%(real_lineno)s'
    logging.basicConfig(filename='log.txt',
                        format=log_format, level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.addFilter(CustomFilter())
    return logger


def log(logger):
    """デコレーターでloggerを引数にとるためのラッパー関数

    Args:
        logger (logging.Logger)

    Returns:
        _decoratorの返り値
    """

    def _decorator(func):
        """デコレーターを使用する関数を引数とする

        Args:
            func (function)

        Returns:
            wrapperの返り値
        """

        # funcのメタデータを引き継ぐ
        @wraps(func)
        def wrapper(*args, **kwargs):
            """実際の処理を書くための関数

            Args:
                *args, **kwargs: funcの引数

            Returns:
                funcの返り値
            """

            func_name = func.__name__
            # loggerで使用するためにfuncに関する情報をdict化
            extra = {
                'real_filename': inspect.getfile(func),
                'real_funcName': func_name,
                'real_lineno': inspect.currentframe().f_back.f_lineno
            }

            logger.info(f'[START] {func_name}', extra=extra)

            try:
                # funcの実行
                func(*args, **kwargs)
            except Exception as err:
                # funcのエラーハンドリング
                logging.error(err, exc_info=True, extra=extra)
                logging.error(f'[KILLED] {func_name}', extra=extra)
                raise ValueError
            else:
                logging.info(f'[ END ] {func_name}', extra=extra)

        return wrapper
    return _decorator
