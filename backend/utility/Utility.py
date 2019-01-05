import os


def check_file_existed(filepath: str):
    if not os.path.isfile(filepath):
        raise Exception("{} not found ".format(filepath))
