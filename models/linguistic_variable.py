from dataclasses import dataclass, field

from models.term import Term


@dataclass
class LinguisticVariable:

    # Название лингвистической переменной
    name: str

    # Максимальное значение предметной шкалы
    # По умолчанию равно 100
    max_value: float = 100

    # Список термов переменной
    # Для каждого нового объекта создаётся собственный пустой список
    terms: list[Term] = field(default_factory=list)

    def to_dict(self):
    # Преобразует объект в словарь для последующего сохранения в JSON

        return {
            "name": self.name,
            "max_value": self.max_value,

            # Каждый объект Term преобразуется в словарь
            "terms": [term.to_dict() for term in self.terms]
        }

    @classmethod
    def from_dict(cls, data):
    # Создаёт объект из словаря, загруженного из JSON

        # Создаём новый объект переменной
        variable = cls(
            name=data["name"],
            max_value=data["max_value"]
        )

        # Восстанавливаем список термов
        variable.terms = [
            Term.from_dict(item)
            for item in data["terms"]
        ]

        return variable