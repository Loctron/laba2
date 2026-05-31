

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QGridLayout
)
from PyQt5.QtCore import Qt
from ui.graph_widget import GraphWidget

from models.linguistic_variable import LinguisticVariable
from models.term import Term

from services.membership_builder import MembershipBuilder
from services.file_manager import FileManager
from services.validator import Validator

from database.database_manager import DatabaseManager


class EditorWindow(QWidget):
    """
    Главное окно редактора лингвистической переменной.

    Позволяет:
    - строить функции принадлежности;
    - редактировать коэффициенты термов;
    - изменять точки на графике;
    - сохранять данные в JSON и БД.
    """

    # ======================================================
    # ИНИЦИАЛИЗАЦИЯ ОКНА
    # ======================================================

    def __init__(
            self,
            variable_name,
            term_names,
            variable=None
    ):
        super().__init__()

        # Основные данные текущей переменной
        self.variable_name = variable_name
        self.term_names = term_names
        self.variable = variable

        # Подключение к БД
        self.db = DatabaseManager()

        # Ссылки на поля ввода коэффициентов
        self.point_edits = []

        # Защита от частичного автосохранения
        self._last_saved_state = None

        # Настройка окна
        self.setWindowTitle(variable_name)
        self.resize(1100, 700)

        # Создание интерфейса
        self.create_ui()

    def validate_terms(self, terms, max_value):
        """Проверка всех термов"""
        return all(Validator.validate(t, max_value) for t in terms)

    # ======================================================
    # СОЗДАНИЕ ПОЛЬЗОВАТЕЛЬСКОГО ИНТЕРФЕЙСА
    # ======================================================

    def create_ui(self):

        # Основной контейнер окна
        layout = QHBoxLayout()

        # --------------------------------------------------
        # Левая часть: график функций принадлежности
        # --------------------------------------------------

        left = QVBoxLayout()

        self.graph = GraphWidget()

        # При перемещении точек на графике
        # таблица должна обновляться автоматически
        self.graph.term_changed.connect(
            self.sync_from_graph
        )

        left.addWidget(self.graph)

        layout.addLayout(left, 4)

        # --------------------------------------------------
        # Правая часть: панель управления
        # --------------------------------------------------

        right = QVBoxLayout()

        # прижимаем элементы вверх
        right.setAlignment(Qt.AlignmentFlag.AlignTop)
        right.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # компактность
        right.setSpacing(8)
        right.setContentsMargins(10, 10, 10, 10)

        # --------------------------------------------------
        # Максимальное значение (label + input в строку)
        # --------------------------------------------------

        max_value_row = QHBoxLayout()

        max_value_label = QLabel("Максимальное значение")

        self.max_value_edit = QLineEdit("100")
        self.max_value_edit.setMaximumWidth(200)

        max_value_row.addWidget(max_value_label)
        max_value_row.addWidget(self.max_value_edit)

        right.addLayout(max_value_row)

        # --------------------------------------------------
        # Кнопки
        # --------------------------------------------------

        self.build_button = QPushButton("Построить")
        self.build_button.setMaximumWidth(200)

        self.save_button = QPushButton("Сохранить")
        self.save_button.setMaximumWidth(200)

        right.addWidget(self.build_button)
        right.addWidget(self.save_button)

        # --------------------------------------------------
        # Таблица коэффициентов
        # --------------------------------------------------

        self.grid = QGridLayout()
        right.addLayout(self.grid)

        # добавление панели в общий layout
        layout.addLayout(right, 1)

        self.setLayout(layout)

        # --------------------------------------------------
        # Подключение сигналов интерфейса
        # --------------------------------------------------

        self.build_button.clicked.connect(
            self.build_graph
        )

        self.save_button.clicked.connect(
            self.save_variable
        )

        # Если открывается существующая переменная,
        # загрузить её данные
        if self.variable:
            self.load_variable_data()

    # ======================================================
    # ЗАПОЛНЕНИЕ ТАБЛИЦЫ КОЭФФИЦИЕНТОВ
    # ======================================================

    def fill_table(self, terms):

        # Очистка старой таблицы
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        self.point_edits.clear()

        # Создание полей ввода для каждого терма
        for row, term in enumerate(terms):

            edits = []

            for value in [
                term.a,
                term.b,
                term.c,
                term.d
            ]:

                edit = QLineEdit(str(value))

                # Изменение значения в таблице
                # сразу обновляет график
                edit.textChanged.connect(
                    self.update_graph
                )

                edits.append(edit)

                self.grid.addWidget(
                    edit,
                    row,
                    len(edits) - 1
                )

            self.point_edits.append(edits)

    # ======================================================
    # СИНХРОНИЗАЦИЯ ТАБЛИЦЫ С ГРАФИКОМ
    # ======================================================

    def sync_from_graph(self):

        # Вызывается при перемещении точек мышью.
        # Коэффициенты автоматически переносятся
        # из графика в таблицу.

        for row, term in enumerate(
            self.graph.terms
        ):

            edits = self.point_edits[row]

            values = [
                term.a,
                term.b,
                term.c,
                term.d
            ]

            for i, value in enumerate(values):

                # Блокировка сигналов предотвращает
                # зацикливание обновлений
                edits[i].blockSignals(True)

                edits[i].setText(
                    str(round(value, 1))
                )

                edits[i].blockSignals(False)

        # Автосохранение изменений
        # self.save_current_state()

    # ======================================================
    # ЗАГРУЗКА СОХРАНЁННОЙ ПЕРЕМЕННОЙ
    # ======================================================

    def load_variable_data(self):

        if self.variable is None:
            return

        self.max_value_edit.setText(
            str(self.variable.max_value)
        )

        self.fill_table(
            self.variable.terms
        )

        self.graph.set_data(
            self.variable.terms,
            self.variable.max_value
        )

    # ======================================================
    # АВТОМАТИЧЕСКОЕ ПОСТРОЕНИЕ ФУНКЦИЙ ПРИНАДЛЕЖНОСТИ
    # ======================================================

    def build_graph(self):

        try:
            # Получаем верхнюю границу шкалы из поля ввода
            max_value = float(
                self.max_value_edit.text()
            )
            # Строим функции принадлежности по заданным именам термов
            terms = MembershipBuilder.build(
                self.term_names,
                max_value
            )

             # Проверяем все термы перед обновлением графика
            if not self.validate_terms(terms, max_value):
                raise ValueError("Некорректные термы")

            # Заполняем таблицу коэффициентов
            self.fill_table(terms)
            # Обновляем график по новым данным
            self.graph.set_data(
                terms,
                max_value
            )

        except ValueError:

            QMessageBox.warning(
                self,
                "Ошибка",
                "Некорректное значение шкалы"
            )

    # ======================================================
    # ОБНОВЛЕНИЕ ГРАФИКА ПО ДАННЫМ ТАБЛИЦЫ
    # ======================================================
    def update_graph(self):
        # Вызывается при изменении любого коэффициента в таблице
        # График автоматически обновляется по новым данным
        try:
            
            max_value = float(
                self.max_value_edit.text()
            )

            terms = []

            for term_name, edits in zip(
                    self.term_names,
                    self.point_edits
            ):

                term = Term(
                    name=term_name,
                    a=float(edits[0].text()),
                    b=float(edits[1].text()),
                    c=float(edits[2].text()),
                    d=float(edits[3].text())
                )

                terms.append(term)

            # Проверяем все термы перед обновлением графика
            if not self.validate_terms(terms, max_value):
                return

            self.graph.terms = terms
            self.graph.max_value = max_value
            self.graph.update()

        except ValueError:
            pass

    # ======================================================
    # ПРОВЕРКА И СОХРАНЕНИЕ ПЕРЕМЕННОЙ
    # ======================================================
    def save_variable(self):
        try:

            max_value = float(
                self.max_value_edit.text()
            )

            terms = []

            for term_name, edits in zip(
                    self.term_names,
                    self.point_edits
            ):
                # Создаём объект терма по данным из таблицы
                term = Term(
                    name=term_name,
                    a=float(edits[0].text()),
                    b=float(edits[1].text()),
                    c=float(edits[2].text()),
                    d=float(edits[3].text())
                )

                if not Validator.validate(
                        term,
                        max_value
                ):

                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        f"Некорректный терм: {term_name}"
                    )

                    return

                terms.append(term)
            # Если все термы корректны, сохраняем переменную в JSON и БД
            variable = LinguisticVariable(
                name=self.variable_name,
                max_value=max_value,
                terms=terms
            )

            path = FileManager.save(
                variable
            )

            self.db.add_variable(
                self.variable_name,
                path
            )

            QMessageBox.information(
                self,
                "Сохранено",
                "Лингвистическая переменная сохранена"
            )

        except ValueError:

            QMessageBox.warning(
                self,
                "Ошибка",
                "Проверьте введённые значения"
            )

    # ======================================================
    # АВТОМАТИЧЕСКОЕ СОХРАНЕНИЕ СОСТОЯНИЯ РЕДАКТОРА
    # ======================================================
    def save_current_state(self):

        try:

            max_value = float(
                self.max_value_edit.text()
            )

            variable = LinguisticVariable(
                name=self.variable_name,
                max_value=max_value,
                terms=self.graph.terms
            )

             # Предотвращение лишних записей
            state_signature = str([(t.a, t.b, t.c, t.d) for t in variable.terms])

            if state_signature == self._last_saved_state:
                return

            self._last_saved_state = state_signature

            path = FileManager.save(variable)
            self.db.add_variable(self.variable_name, path)

        except Exception:
            pass