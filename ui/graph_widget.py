from PyQt5.QtCore import pyqtSignal, QPoint
from PyQt5.QtGui import (
    QPainter,
    QPen,
    QColor,
    QPolygon
)
from PyQt5.QtWidgets import QWidget


class GraphWidget(QWidget):
    """
    Виджет отображения функций принадлежности.

    Возможности:
    - отрисовка трапециевидных функций принадлежности;
    - отображение степени принадлежности курсора;
    - перемещение отдельных контрольных точек;
    - перемещение терма целиком;
    - автоматическая синхронизация с таблицей коэффициентов.
    """
    # Сигнал, который испускается при изменении терма
    term_changed = pyqtSignal()

    # Радиус круга для перетаскивания контрольных точек
    HANDLE_RADIUS = 6

    # ======================================================
    # ИНИЦИАЛИЗАЦИЯ ВИДЖЕТА
    # ======================================================

    def __init__(self):
        super().__init__()

        # Изначально нет термов, верхняя граница шкалы - 100
        self.terms = []
        self.max_value = 100

        self.active_term = None
        self.active_point = None

        self.drag_whole_term = False
        self.drag_start_x = 0
        # Сохранение исходных координат терма при начале перетаскивания
        self.drag_original = (0, 0, 0, 0)

        # Текст для отображения степени принадлежности при наведении курсора
        self.hover_text = ""

        # Набор цветов для разных термов
        self.colors = [
            QColor(220, 20, 60),
            QColor(30, 144, 255),
            QColor(50, 205, 50),
            QColor(255, 140, 0),
            QColor(148, 0, 211),
            QColor(0, 206, 209),
            QColor(255, 105, 180),
            QColor(139, 69, 19)
        ]

        # Отслеживание движения мыши без нажатия
        self.setMouseTracking(True)
        # Минимальная высота области рисования
        self.setMinimumHeight(450)

    # ======================================================
    # ЗАГРУЗКА ДАННЫХ ДЛЯ ОТОБРАЖЕНИЯ
    # ======================================================
    def set_data(self, terms, max_value):

        self.terms = terms
        self.max_value = max_value

        self.update()

    # ======================================================
    # ПРЕОБРАЗОВАНИЕ ЗНАЧЕНИЙ В КООРДИНАТЫ ЭКРАНА
    # ======================================================
    def value_to_x(self, value):
        # Перевод значения предметной шкалы
        # в координату X на экране.

        margin = 40

        width = self.width() - margin * 2

        return (
            margin +
            value / self.max_value * width
        )

    # ======================================================
    # ПРЕОБРАЗОВАНИЕ КООРДИНАТ ЭКРАНА В ЗНАЧЕНИЕ ШКАЛЫ
    # ======================================================
    def x_to_value(self, x):
    # Используется при перемещении мыши
    # для вычисления нового значения точки.

        margin = 40

        width = self.width() - margin * 2

        value = (
            (x - margin) / width
        ) * self.max_value

        return max(
            0,
            min(value, self.max_value)
        )

    # ======================================================
    # ВЫЧИСЛЕНИЕ ЭКРАННЫХ КООРДИНАТ ТОЧЕК a,b,c,d
    # ======================================================
    def point_positions(self, term):
    # Возвращает положение всех контрольных точек
    # трапециевидной функции принадлежности.

        h = self.height()

        margin = 40

        bottom = h - margin
        top = margin

        return {
            "a": (
                self.value_to_x(term.a),
                bottom
            ),
            "b": (
                self.value_to_x(term.b),
                top
            ),
            "c": (
                self.value_to_x(term.c),
                top
            ),
            "d": (
                self.value_to_x(term.d),
                bottom
            )
        }

    # ======================================================
    # ВЫЧИСЛЕНИЕ СТЕПЕНИ ПРИНАДЛЕЖНОСТИ μ(x)
    # ======================================================
    def membership_value(self, term, x):

        if x <= term.a:
            return 0

        if term.a < x < term.b:

            if term.b == term.a:
                return 1

            return (
                (x - term.a)
                /
                (term.b - term.a)
            )

        if term.b <= x <= term.c:
            return 1

        if term.c < x < term.d:

            if term.d == term.c:
                return 1

            return (
                (term.d - x)
                /
                (term.d - term.c)
            )

        return 0

    # ======================================================
    # ПРОВЕРКА ПОПАДАНИЯ КУРСОРА ВНУТРЬ ТЕРМА
    # ======================================================
    def inside_term(
            self,
            term,
            x,
            y
    ):

        pos = self.point_positions(term)

        left = pos["a"][0]
        right = pos["d"][0]

        top = 40
        bottom = self.height() - 40

        return (
            left <= x <= right
            and top <= y <= bottom
        )

    # ======================================================
    # НОРМАЛИЗАЦИЯ СОСЕДНИХ ТЕРМОВ
    # ======================================================
    def normalize_terms(self):
        # Если термов меньше 2, нормализация не требуется

        if len(self.terms) < 2:
            return
        # Проходим по всем парам соседних термов и выравниваем
        for i in range(
                len(self.terms) - 1
        ):
            
            left = self.terms[i]
            right = self.terms[i + 1]

            # Общая граница вычисляется как середина
            # между правой границей левого терма
            # и левой границей правого терма.
            middle = (
                left.d +
                right.a
            ) / 2

            left.d = middle
            right.a = middle

    # ======================================================
    # ОТРИСОВКА ГРАФИКА
    # ======================================================
    def paintEvent(self, event):

        painter = QPainter(self)

        # Заливаем фон белым цветом
        painter.fillRect(
            self.rect(),
            QColor("white")
        )
        # Рисуем рамку и шкалу
        w = self.width()
        h = self.height()

        margin = 40

        bottom = h - margin

        painter.setPen(QColor("black"))

        painter.drawRect(
            margin,
            margin,
            w - margin * 2,
            h - margin * 2
        )

        # Рисуем деления шкалы и подписи
        scale_x = (
            w - margin * 2
        ) / self.max_value

    
        for i in range(11):

            value = (
                self.max_value / 10
            ) * i

            x = (
                margin +
                value * scale_x
            )
        
            painter.drawLine(
                int(x),
                bottom,
                int(x),
                bottom + 5
            )
        
            painter.drawText(
                int(x) - 10,
                bottom + 20,
                str(int(value))
            )
        # Рисуем функции принадлежности
        for index, term in enumerate(
                self.terms
        ):

            color = self.colors[
                index % len(self.colors)
            ]

            pen = QPen(color)
            pen.setWidth(2)

            painter.setPen(pen)

            pos = self.point_positions(term)

            # Рисуем многоугольник трапециевидной функции принадлежности 
            polygon = QPolygon([

                QPoint(
                    int(pos["a"][0]),
                    int(pos["a"][1])
                ),

                QPoint(
                    int(pos["b"][0]),
                    int(pos["b"][1])
                ),

                QPoint(
                    int(pos["c"][0]),
                    int(pos["c"][1])
                ),

                QPoint(
                    int(pos["d"][0]),
                    int(pos["d"][1])
                )
            ])

            # Заливаем многоугольник полупрозрачным цветом
            fill = QColor(color)
            fill.setAlpha(60)

            # Устанавливаем кисть для заливки
            painter.setBrush(fill)

            # Рисуем многоугольник
            painter.drawPolygon(polygon)

            points = [
                pos["a"],
                pos["b"],
                pos["c"],
                pos["d"]
            ]

            # Рисуем линии между точками a,b,c,d
            for i in range(3):

                painter.drawLine(
                    int(points[i][0]),
                    int(points[i][1]),
                    int(points[i + 1][0]),
                    int(points[i + 1][1])
                )

            painter.setBrush(color)

            # Рисуем круги для перетаскивания контрольных точек
            for point in pos.values():

                painter.drawEllipse(
                    int(point[0]) - self.HANDLE_RADIUS,
                    int(point[1]) - self.HANDLE_RADIUS,
                    self.HANDLE_RADIUS * 2,
                    self.HANDLE_RADIUS * 2
                )

            # Рисуем название терма над его центром
            painter.setPen(QColor("black"))

            center = (
                self.value_to_x(term.b) +
                self.value_to_x(term.c)
            ) / 2

            painter.drawText(
                int(center - 40),
                25,
                term.name
            )

        # Подсветка области между соседними термами для визуального разделения
        # for i in range(
        #         len(self.terms) - 1
        # ):

        #     left = self.terms[i]
        #     right = self.terms[i + 1]

        #     x1 = self.value_to_x(left.d)
        #     x2 = self.value_to_x(right.a)

        #     painter.fillRect(
        #         int(min(x1, x2)),
        #         margin,
        #         int(abs(x2 - x1)),
        #         h - margin * 2,
        #         QColor(
        #             255,
        #             255,
        #             0,
        #             70
        #         )
        #     )

        # Отображение степени принадлежности при наведении курсора
        if self.hover_text:

            painter.setPen(QColor(0, 0, 0))

            painter.drawText(
                10,
                h - 10,
                self.hover_text
            )

    # ======================================================
    # ОБРАБОТКА НАЖАТИЯ КНОПКИ МЫШИ
    # ======================================================
    def mousePressEvent(self, event):
        
        # Получаем координаты клика мыши
        x = event.x()
        y = event.y()

        # Сначала проверяем, не кликнули ли мы по контрольной точке
        for term_index, term in enumerate(
                self.terms
        ):

            positions = self.point_positions(
                term
            )
            # Проверяем каждую контрольную точку терма
            for point_name, point in positions.items():

                px, py = point

                dx = x - px
                dy = y - py
                # Если расстояние от клика до точки меньше радиуса круга, 
                # активируем эту точку для перетаскивания
                if (
                    dx * dx +
                    dy * dy
                ) <= (
                    self.HANDLE_RADIUS * 2
                ) ** 2:

                    self.active_term = term_index
                    self.active_point = point_name

                    return
        # Если не кликнули по контрольной точке, 
        # проверяем, не кликнули ли по самому терму
        for term_index, term in enumerate(
                self.terms
        ):

            if self.inside_term(
                    term,
                    x,
                    y
            ):

                self.drag_whole_term = True

                self.active_term = term_index

                self.drag_start_x = x

                self.drag_original = (
                    term.a,
                    term.b,
                    term.c,
                    term.d
                )

                return

    # ======================================================
    # ОБРАБОТКА ПЕРЕМЕЩЕНИЯ МЫШИ
    # ======================================================    
    def mouseMoveEvent(self, event):
        # Если нет активного терма, 
        #  отображаем степень принадлежности курсора
        if self.active_term is None:

            value = self.x_to_value(
                event.x()
            )

            texts = []

            for term in self.terms:

                mu = self.membership_value(
                    term,
                    value
                )

                if mu > 0:

                    texts.append(
                        f"{term.name}: {mu:.2f}"
                    )

            self.hover_text = " | ".join(
                texts
            )

            self.update()

            return

        # Если перетаскиваем весь терм, 
        # вычисляем смещение и применяем его ко всем точкам терма
        if self.drag_whole_term:

            delta = (
                self.x_to_value(event.x())
                -
                self.x_to_value(
                    self.drag_start_x
                )
            )

            term = self.terms[
                self.active_term
            ]

            new_a = (
                self.drag_original[0]
                + delta
            )

            new_b = (
                self.drag_original[1]
                + delta
            )

            new_c = (
                self.drag_original[2]
                + delta
            )

            new_d = (
                self.drag_original[3]
                + delta
            )

            if new_a < 0:
                return

            if new_d > self.max_value:
                return

            term.a = new_a
            term.b = new_b
            term.c = new_c
            term.d = new_d

            self.normalize_terms()

            self.update()

            self.term_changed.emit()

            return
        # Если перетаскиваем отдельную точку,
        # вычисляем новое значение точки по координате мыши
        value = self.x_to_value(
            event.x()
        )

        term = self.terms[
            self.active_term
        ]
        # В зависимости от активной точки, обновляем её значение,
        # при этом соблюдая порядок a ≤ b ≤ c ≤ d
        if self.active_point == "a":

            term.a = min(
                value,
                term.b
            )
        elif self.active_point == "b":

            term.b = max(
                term.a,
                min(
                    value,
                    term.c
                )
            )

        elif self.active_point == "c":

            term.c = max(
                term.b,
                min(
                    value,
                    term.d
                )
            )

        elif self.active_point == "d":

            term.d = max(
                value,
                term.c
            )

        self.normalize_terms()

        self.update()

        self.term_changed.emit()

    # ======================================================
    # ЗАВЕРШЕНИЕ ПЕРЕТАСКИВАНИЯ
    # ======================================================
    def mouseReleaseEvent(self, event):

        self.active_term = None
        self.active_point = None

        self.drag_whole_term = False