import sqlite3  # Модуль для работы с базой данных SQLite


class DatabaseManager:
    # Класс для управления базой данных лингвистических переменных.

    def __init__(self):
        """
        Конструктор класса.
        Создаёт подключение к базе данных и курсор для выполнения SQL-запросов.
        Если файла базы данных нет, он будет создан автоматически.
        """

        # Подключение к базе данных
        self.connection = sqlite3.connect("fuzzy.db")

        # Создание курсора для выполнения SQL-команд
        self.cursor = self.connection.cursor()

        # Создание необходимых таблиц
        self.create_tables()

    def create_tables(self):
    # Создаёт таблицу linguistic_variables, если она ещё не существует.

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS linguistic_variables
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                name TEXT UNIQUE,                      
                file_path TEXT                        
            )
        """)

        # Сохраняем изменения в базе данных
        if self.connection:
            self.connection.commit()

    def add_variable(self, name, path):
    # Добавляет или обновляет запись о лингвистической переменной в базе данных.

        self.cursor.execute(
            """
            INSERT OR REPLACE INTO linguistic_variables
            (name, file_path)
            VALUES (?, ?)
            """,
            (name, path)
        )

        # Сохраняем изменения
        if self.connection:
            self.connection.commit()

    def get_variable(self, name):
    # Возвращает путь к файлу по имени лингвистической переменной

        self.cursor.execute(
            """
            SELECT file_path
            FROM linguistic_variables
            WHERE name=?
            """,
            (name,)
        )

        return self.cursor.fetchone()

    def get_all_variables(self):
    # Возвращает список всех имён лингвистических переменных

        self.cursor.execute(
            """
            SELECT name
            FROM linguistic_variables
            ORDER BY name
            """
        )

        # Из результата запроса берём только первый столбец каждой строки
        return [row[0] for row in self.cursor.fetchall()]
    
    # Закрытие соединения
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close()