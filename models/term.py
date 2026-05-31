from dataclasses import dataclass


# Класс Term описывает один терм лингвистической переменной
@dataclass
class Term:

    # Название терма
    name: str

    # Параметры трапециевидной функции принадлежности
    # a и d — точки, где функция равна 0
    # b и c — точки, где функция равна 1
    a: float = 0
    b: float = 0
    c: float = 0
    d: float = 0

    def to_dict(self):
    # Преобразует объект Term в словарь

        return {
            "name": self.name,
            "a": self.a,
            "b": self.b,
            "c": self.c,
            "d": self.d
        }

    @classmethod
    def from_dict(cls, data):
    # Создает объект Term из словаря

        return cls(
            name=data["name"],
            a=data["a"],
            b=data["b"],
            c=data["c"],
            d=data["d"]
        )