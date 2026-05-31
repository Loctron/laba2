from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSpinBox,
    QMessageBox
)

from ui.editor_window import EditorWindow

from database.database_manager import DatabaseManager
from services.file_manager import FileManager


class MainWindow(QWidget):
    """
    Главное окно приложения.

    Позволяет:
    - создать новую лингвистическую переменную;
    - указать количество термов;
    - ввести названия термов;
    - открыть редактор функций принадлежности;
    - загрузить ранее сохранённую переменную.
    """

    # ======================================================
    # ИНИЦИАЛИЗАЦИЯ ГЛАВНОГО ОКНА
    # ======================================================

    def __init__(self):

        super().__init__()

        # Подключение базы данных

        self.db = DatabaseManager()

        # Ссылка на окно редактора
        self.editor = None

        # Список полей ввода названий термов
        self.term_edits = []

        # Настройка окна
        self.setWindowTitle(
            "Редактор лингвистических переменных"
        )

        self.resize(800, 500)

        # Создание интерфейса
        self.create_ui()

    # ======================================================
    # СОЗДАНИЕ ПОЛЬЗОВАТЕЛЬСКОГО ИНТЕРФЕЙСА
    # ======================================================

    def create_ui(self):

        # Основной вертикальный контейнер
        layout = QVBoxLayout()

        # --------------------------------------------------
        # Блок выбора имени переменной
        # --------------------------------------------------

        row1 = QHBoxLayout()

        row1.addWidget(
            QLabel(
                "Имя лингвистической переменной"
            )
        )

        # Поле ввода имени переменной
        self.name_edit = QLineEdit()

        row1.addWidget(
            self.name_edit
        )

        # Кнопка загрузки существующей переменной
        self.load_button = QPushButton(
            "Загрузить"
        )

        row1.addWidget(
            self.load_button
        )

        layout.addLayout(row1)

        # --------------------------------------------------
        # Блок задания количества термов
        # --------------------------------------------------

        row2 = QHBoxLayout()

        row2.addWidget(
            QLabel("Количество термов")
        )

        # Счётчик количества термов
        self.term_count = QSpinBox()

        # Ограничение количества термов
        self.term_count.setMinimum(2)
        self.term_count.setMaximum(20)

        row2.addWidget(
            self.term_count
        )

        # Кнопка создания полей ввода термов
        self.create_terms_button = QPushButton(
            "Задать"
        )

        row2.addWidget(
            self.create_terms_button
        )

        layout.addLayout(row2)

        # --------------------------------------------------
        # Область ввода названий термов
        # --------------------------------------------------

        self.terms_layout = QVBoxLayout()

        layout.addLayout(
            self.terms_layout
        )

        # --------------------------------------------------
        # Кнопка открытия редактора
        # --------------------------------------------------

        self.build_button = QPushButton(
            "Построить"
        )

        layout.addWidget(
            self.build_button
        )

        self.setLayout(layout)

        # --------------------------------------------------
        # Подключение сигналов кнопок
        # --------------------------------------------------

        self.create_terms_button.clicked.connect(
            self.create_term_fields
        )

        self.build_button.clicked.connect(
            self.open_editor
        )

        self.load_button.clicked.connect(
            self.load_variable
        )

    # ======================================================
    # СОЗДАНИЕ ПОЛЕЙ ВВОДА НАЗВАНИЙ ТЕРМОВ
    # ======================================================

    def create_term_fields(self):

        # Удаление ранее созданных полей
        while self.terms_layout.count():

            item = self.terms_layout.takeAt(0)

            if item:
                widget = item.widget()

                if widget:
                    widget.deleteLater()

        # Очистка списка ссылок на поля
        self.term_edits.clear()

        # Получение количества термов
        count = self.term_count.value()

        # Создание необходимого числа полей ввода
        for i in range(count):

            edit = QLineEdit(
                f"Терм {i + 1}"
            )

            self.term_edits.append(edit)

            self.terms_layout.addWidget(
                edit
            )

    # ======================================================
    # СОЗДАНИЕ НОВОЙ ЛИНГВИСТИЧЕСКОЙ ПЕРЕМЕННОЙ
    # ======================================================

    def open_editor(self):

        # Получение имени переменной
        name = self.name_edit.text().strip()

        # Проверка заполнения имени
        if not name:

            QMessageBox.warning(
                self,
                "Ошибка",
                "Введите имя переменной"
            )

            return

        # Формирование списка имён термов
        term_names = [
            edit.text().strip()
            for edit in self.term_edits
        ]

        # Открытие окна редактора
        self.editor = EditorWindow(
            variable_name=name,
            term_names=term_names
        )

        self.editor.show()

    # ======================================================
    # ЗАГРУЗКА СОХРАНЁННОЙ ПЕРЕМЕННОЙ
    # ======================================================

    def load_variable(self):

        # Получение имени переменной
        name = self.name_edit.text().strip()

        if not name:
            return

        # --------------------------------------------------
        # Поиск записи в базе данных
        # --------------------------------------------------

        result = self.db.get_variable(name)

        if not result:

            QMessageBox.warning(
                self,
                "Ошибка",
                "Переменная не найдена"
            )

            return

        # --------------------------------------------------
        # Загрузка JSON-файла переменной
        # --------------------------------------------------

        variable = FileManager.load(
            result[0]
        )

        # --------------------------------------------------
        # Восстановление списка термов
        # --------------------------------------------------

        self.term_count.setValue(
            len(variable.terms)
        )

        self.create_term_fields()

        for edit, term in zip(
                self.term_edits,
                variable.terms
        ):

            edit.setText(term.name)

        # --------------------------------------------------
        # Открытие редактора с загруженными данными
        # --------------------------------------------------

        self.editor = EditorWindow(
            variable_name=variable.name,

            term_names=[
                term.name
                for term in variable.terms
            ],

            variable=variable
        )

        self.editor.show()