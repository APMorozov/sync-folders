import hashlib


def hash_file_sha1(path: str) -> str:
    """
    Вычисление хэша файлы
    :param path: путь к файлу
    :return: хэш
    """
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
