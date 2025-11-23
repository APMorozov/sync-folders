import json


"""Модуль для работы с файлами"""


def read_json(path: str) -> dict:
    """
    Чтение json файла
    :param path: путь к JSON файлу
    :return: tuple данных
    """
    try:
        with open(path, mode="r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as not_found:
        raise FileNotFoundError(f"File was not found: {not_found}")
    except json.JSONDecodeError as decode_error:
        raise ValueError(f"Error decoded the json file: {decode_error}")
    except Exception as exc:
        raise Exception(f"An error occurred when opening the file {exc}")


def write_json(path: str, data: dict) -> None:
    """
    write data to json file
    :param path: path to json file
    :param data: data to file
    :return: None
    """
    try:
        with open(path, mode="w", encoding="utf-8") as file:
            return json.dump(data, file, indent=4)
    except FileNotFoundError as not_found:
        raise FileNotFoundError(f"File was not found: {not_found}")
    except Exception as exc:
        raise Exception(f"An error occurred when opening the file {exc}")