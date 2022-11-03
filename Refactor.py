#vacancies_medium.csv
import csv
import codecs
import re
import enum
from prettytable import PrettyTable
from datetime import datetime
from typing import Generator

CLEANER = re.compile('<.*?>')
SPACE_CLEANER = re.compile('(\s\s+)|(\xa0)')
TRANSLATION_EXPERIENCE = {
    "noExperience": "Нет опыта",
    "between1And3": "От 1 года до 3 лет",
    "between3And6": "От 3 до 6 лет",
    "moreThan6": "Более 6 лет"
}
TRANSLATION_CURRENCY = {
    "AZN": "Манаты",
    "BYR": "Белорусские рубли",
    "EUR": "Евро",
    "GEL": "Грузинский лари",
    "KGS": "Киргизский сом",
    "KZT": "Тенге",
    "RUR": "Рубли",
    "UAH": "Гривны",
    "USD": "Доллары",
    "UZS": "Узбекский сум",
}
TRANSLATION_PREMIUM = {
    "False": "Нет",
    "True": "Да"
}
TRANSLATION_GROSS = {
    "False": "С вычетом налогов",
    "True": "Без вычета налогов"
}


class HeadKey(enum.Enum):
    name = "Название"
    description = "Описание"
    key_skills = "Навыки"
    experience_id = "Опыт работы"
    premium = "Премиум-вакансия"
    employer_name = "Компания"
    salary_from = "Нижняя граница вилки оклада"
    salary_to = "Верхняя граница вилки оклада"
    salary_gross = "Оклад указан до вычета налогов"
    salary_currency = "Идентификатор валюты оклада"
    area_name = "Название региона"
    published_at = "Дата публикации вакансии"
    salary = "Оклад"


def format_float(salary: str) -> str:
    return "{:,.0f}".format(float(salary)).replace(',', ' ')


def validate(element: list, properties_count: int) -> bool:
    if len(element) != properties_count - 1:
        return False
    for i in range(len(element)):
        if element[i].replace(' ', '') == '':
            return False
    return True


def clean_properties(merits: list) -> list:
    result = []
    for merit in merits:
        temp_property = merit.replace("\r\n", '\n')
        temp_property = temp_property.split('\n')
        for i in range(len(temp_property)):
            temp_property[i] = temp_property[i].strip(' ')
            temp_property[i] = re.sub(CLEANER, '', temp_property[i])
            temp_property[i] = re.sub(SPACE_CLEANER, ' ', temp_property[i])
        result.append(temp_property)
    return result


def make_dictionary(keys: list, values: list) -> dict:
    keys = list(map(lambda x: HeadKey.__getitem__(x), keys))
    result = dict(zip(keys, values))
    return result


def get_salary(vacancy: dict) -> str:
    salary = "{0} - {1} ({2}) ({3})".format(
        format_float(vacancy[HeadKey.salary_from][0]),
        format_float(vacancy[HeadKey.salary_to][0]),
        TRANSLATION_CURRENCY[vacancy[HeadKey.salary_currency][0]],
        TRANSLATION_GROSS[vacancy[HeadKey.salary_gross][0]]
    )
    return salary


def csv_filer(reader: list, list_naming: list) -> Generator[dict, None, None]:
    for line in reader:
        if validate(line, len(list_naming)):
            yield make_dictionary(list_naming, clean_properties(line))


def csv_reader(file_name: str) -> list:
    reader = csv.reader(codecs.open(file_name, "r", "utf_8_sig"), delimiter=',')
    reader.__next__()
    return list(reader)


def make_table_row(row: dict) -> list:
    for row_value in row.values():
        row_value = row_value[0]
        if len(row_value) > 100:
            row_value = row_value[:100] + "..."
        yield row_value


def formatter(row: dict) -> list:
    datetime_obj = datetime.strptime(row[HeadKey.published_at][0], "%Y-%m-%dT%H:%M:%S%z")

    row[HeadKey.description] = [", ".join(row[HeadKey.description])]
    row[HeadKey.key_skills] = ["\n".join(row[HeadKey.key_skills])]
    row[HeadKey.premium][0] = TRANSLATION_PREMIUM[row[HeadKey.premium][0].capitalize()]
    row[HeadKey.experience_id][0] = TRANSLATION_EXPERIENCE[row[HeadKey.experience_id][0]]
    row[HeadKey.published_at][0] = datetime.strftime(datetime_obj, "%d.%m.%Y")

    row_as_list = list(row.items())
    row_as_list.insert(6, (HeadKey.salary, [get_salary(row)]))
    row = dict(row_as_list)
    del row[HeadKey.salary_from]
    del row[HeadKey.salary_to]
    del row[HeadKey.salary_gross]
    del row[HeadKey.salary_currency]

    return list(make_table_row(row))


def print_vacancies(data_vacancies: Generator[dict, None, None]) -> None:
    my_table = PrettyTable()
    row_count = 0

    for vacancy in data_vacancies:
        row_count += 1
        my_table.add_row([row_count] + formatter(vacancy))

    my_table.hrules = 1
    my_table.field_names = [
        "№",
        HeadKey.name.value,
        HeadKey.description.value,
        HeadKey.key_skills.value,
        HeadKey.experience_id.value,
        HeadKey.premium.value,
        HeadKey.employer_name.value,
        HeadKey.salary.value,
        HeadKey.area_name.value,
        HeadKey.published_at.value
    ]
    my_table.max_width = 20
    my_table.min_width = 20
    my_table._min_width = {"№": 0}
    my_table.align = 'l'
    print(my_table)


try:
    vacancies = csv_reader(input() or "vacancies_medium.csv")
    if len(vacancies) == 0:
        print("Нет данных")
    else:
        print_vacancies(csv_filer(vacancies, list(HeadKey.__members__)))
except StopIteration:
    print("Пустой файл")
