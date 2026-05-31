from models.term import Term


class MembershipBuilder:
    """
    Класс для автоматического построения
    трапециевидных функций принадлежности.

    На вход получает:
    - список имён термов;
    - максимальное значение шкалы.

    На выходе возвращает список объектов Term
    с автоматически рассчитанными параметрами a, b, c, d.
    """

    @staticmethod
    def build(term_names, max_value):
    # Построение термов по заданным именам и максимальному значению шкалы

        # Количество термов
        count = len(term_names)

        # Для построения требуется минимум два терма
        if count < 2:
            raise ValueError("Минимум должно быть 2 терма")

        # Ширина одного интервала шкалы
        step = max_value / count

        # Половина интервала
        half = step / 2

        # Список будущих термов
        terms = []

        # Перебираем все названия термов
        for i, name in enumerate(term_names):

            # Первый терм
            if i == 0:

                a = 0
                b = 0
                c = half
                d = step

            # Последний терм
            elif i == count - 1:

                a = max_value - step - half
                b = max_value - step
                c = max_value
                d = max_value

            # Все промежуточные термы
            else:

                a = i * step - half
                b = i * step
                c = i * step + half
                d = i * step + step

            # Создаём объект Term
            terms.append(
                Term(
                    name=name,

                    # Округляем значения до целых
                    a=round(a),
                    b=round(b),
                    c=round(c),
                    d=round(d)
                )
            )

        # Возвращаем список термов
        return terms