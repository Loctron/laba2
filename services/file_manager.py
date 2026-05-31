import json
import os

from models.linguistic_variable import LinguisticVariable


# Каталог, в котором будут храниться все сохранённые переменные
STORAGE_DIR = "storage"


class FileManager:
    # Класс для сохранения и загрузки лингвистических переменных в JSON-файлах

    @staticmethod
    def save(variable: LinguisticVariable):
    # Сохраняет лингвистическую переменную в JSON-файл

        # Создаёт папку storage, если её ещё нет
        os.makedirs(STORAGE_DIR, exist_ok=True)

        # Формирует полный путь к файлу
        path = os.path.join(
            STORAGE_DIR,
            f"{variable.name}.json"
        )

        # Открывает файл для записи
        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            # Преобразует объект в словарь
            # и сохраняет его в JSON-файл
            json.dump(
                variable.to_dict(),
                file,
                indent=4,          # красивое форматирование
                ensure_ascii=False # сохранение русских символов
            )

        # Возвращает путь к сохранённому файлу
        return path

    @staticmethod
    def load(path):
    # Загружает лингвистическую переменную из JSON-файла

        # Открывает файл для чтения
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            # Загружает JSON в словарь Python
            data = json.load(file)

        # Создаёт объект из считанных данных
        return LinguisticVariable.from_dict(data)