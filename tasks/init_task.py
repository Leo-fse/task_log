import settings
import os


def _make_dir():
    # exist_ok = True: 既に存在しているディレクトリを指定してもエラーにならない
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)


def main():
    _make_dir()


if __name__ == "__main__":
    main()
