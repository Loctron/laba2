class Validator:
    # Класс для проверки корректности данных, введённых пользователем

    @staticmethod
    def validate(term, max_value):

        # Проверяем правильный порядок точек:
        # a ≤ b ≤ c ≤ d
        #
        # Для трапециевидной функции принадлежности
        # точки должны располагаться строго слева направо.
        if not (
            term.a <= term.b <= term.c <= term.d
        ):
            return False

        # Проверяем каждое значение коэффициентов
        for value in (
            term.a,
            term.b,
            term.c,
            term.d
        ):

            # Значение не должно быть отрицательным
            if value < 0:
                return False

            # Значение не должно выходить
            # за пределы предметной шкалы
            if value > max_value:
                return False

        return True