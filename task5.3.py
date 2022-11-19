import csv
import codecs
import re
from datetime import datetime
from prettytable import PrettyTable
from typing import List, Generator, Callable


class SortParameterError(BaseException):
    pass


class SortWayError(BaseException):
    pass


class OutOfDataError(BaseException):
    pass


class Translator:
    translation_currency = {
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
    translation_gross = {
        "False": "С вычетом налогов",
        "True": "Без вычета налогов"
    }
    translation_filter = {
        "Навыки": "key_skills",
        "Оклад": "salary",
        "Дата публикации вакансии": "published_at",
        "Опыт работы": "experience_id",
        "Премиум-вакансия": "premium",
        "Идентификатор валюты оклада": "salary_currency",
        "Название": "name",
        "Название региона": "area_name",
        "Компания": "employer_name",
        "Описание": "description"
    }
    translation_experience = {
        "noExperience": "Нет опыта",
        "between1And3": "От 1 года до 3 лет",
        "between3And6": "От 3 до 6 лет",
        "moreThan6": "Более 6 лет"
    }
    experience_to_int = {
        "noExperience": 1,
        "between1And3": 2,
        "between3And6": 3,
        "moreThan6": 4
    }
    translation_premium = {
        "False": "Нет",
        "True": "Да"
    }
    currency_to_rub = {
        "AZN": 35.68,
        "BYR": 23.91,
        "EUR": 59.90,
        "GEL": 21.74,
        "KGS": 0.76,
        "KZT": 0.13,
        "RUR": 1,
        "UAH": 1.64,
        "USD": 60.66,
        "UZS": 0.0055,
    }

    @staticmethod
    def inverse_dict(straight: dict) -> dict:
        return {v: k for k, v in straight.items()}


class Salary:
    def __init__(self, salary_property: List[str]):
        self.salary_from = salary_property[1]
        self.salary_to = salary_property[2]
        self.salary_gross = salary_property[3]
        self.salary_currency = salary_property[4]

    def __str__(self):
        return "{0} - {1} ({2}) ({3})".format(
            self.__format_float(self.salary_from),
            self.__format_float(self.salary_to),
            Translator.translation_currency[self.salary_currency],
            Translator.translation_gross[self.salary_gross]
        )

    @staticmethod
    def __format_float(salary: str) -> str:
        return "{:,.0f}".format(float(salary)).replace(',', ' ')


class Vacancy:
    __formatter = {
        lambda row: row.__setattr__("description", row.description.strip()),
        lambda row: row.__setattr__("key_skills", "\n".join(row.key_skills)),
        lambda row: row.__setattr__("premium", Translator.translation_premium[row.premium.capitalize()]),
        lambda row: row.__setattr__("experience_id", Translator.translation_experience[row.experience_id]),
        lambda row: row.__setattr__("published_at", datetime.strftime(row.published_at, "%d.%m.%Y"))
    }

    def __init__(self, property_list: List[any]):
        self.name = property_list[0]
        self.description = property_list[1]
        self.key_skills = property_list[2] if type(property_list[2]) == list else [property_list[2]]
        self.experience_id = property_list[3]
        self.premium = property_list[4]
        self.employer_name = property_list[5]
        self.salary = Salary(property_list[5:10])
        self.area_name = property_list[10]
        self.published_at = datetime.strptime(property_list[11], "%Y-%m-%dT%H:%M:%S%z")

    def make_table_row(self) -> List[any]:
        result = []
        for formatting in self.__formatter:
            formatting(self)

        for attribute in self.__dict__:
            attribute_value = self.__getattribute__(attribute)
            if len(attribute_value.__str__()) > 100:
                attribute_value = attribute_value.__str__()[:100] + "..."
            result.append(attribute_value)
        return result


class DataSet:
    __CLEANER = re.compile('<.*?>')
    __SPACE_CLEANER = re.compile('(\s\s+)|(\xa0)')
    __sorter = {
        "Навыки": lambda to_sort:
        len(to_sort.key_skills),
        "Оклад": lambda to_sort:
        (float(to_sort.salary.salary_from) + float(to_sort.salary.salary_to))
        / 2 * Translator.currency_to_rub[to_sort.salary.salary_currency],
        "Опыт работы": lambda to_sort:
        Translator.experience_to_int[to_sort.experience_id],
        "Название": lambda to_sort:
        to_sort.name,
        "Описание": lambda to_sort:
        to_sort.description,
        "Премиум-вакансия": lambda to_sort:
        to_sort.premium,
        "Компания": lambda to_sort:
        to_sort.employer_name,
        "Название региона": lambda to_sort:
        to_sort.area_name,
        "Дата публикации вакансии": lambda to_sort:
        to_sort.published_at
    }

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.vacancies_reader = self.__clean_properties(
            vacancies=self.__reader(file_name=file_name)
        )

    @staticmethod
    def __reader(file_name: str) -> csv.reader:
        reader = csv.reader(open(file_name), delimiter=',')
        reader.__next__()
        return reader

    @staticmethod
    def __validate(element: List[str]) -> bool:
        if len(element) == 0:
            return False
        for i in range(len(element)):
            if element[i] == '':
                return False
        return True

    def __clean_properties(self, vacancies: csv.reader) -> Generator[Vacancy, None, None]:
        i = 0
        for vacancy in vacancies:
            i += 1
            clean_vacancy = []
            if self.__validate(element=vacancy):
                for merit_index in range(len(vacancy)):
                    if merit_index == 2:
                        temp_property = vacancy[merit_index].split('\n')
                        for i in range(len(temp_property)):
                            temp_property[i] = re.sub(self.__CLEANER, '', temp_property[i])
                            temp_property[i] = re.sub(self.__SPACE_CLEANER, ' ', temp_property[i]).strip()
                    else:
                        temp_property = re.sub(self.__CLEANER, '', vacancy[merit_index])
                        temp_property = re.sub(self.__SPACE_CLEANER, ' ', temp_property).strip()
                    clean_vacancy.append(temp_property)
                yield Vacancy(clean_vacancy)
        if i == 0:
            raise OutOfDataError

    def get_sorted(self, sort_parameter: Callable, is_revers: bool) -> List[Vacancy] or Generator[Vacancy, None, None]:
        if sort_parameter == "":
            return self.vacancies_reader
        elif self.__sorter.__contains__(sort_parameter):
            sort_key = self.__sorter[sort_parameter]
        else:
            raise SortParameterError
        return sorted(list(self.vacancies_reader), key=sort_key, reverse=is_revers)


class InputConnect:
    def __init__(
            self,
            filename,
            filter_parameter,
            sort_parameter,
            is_revers,
            print_range,
            print_columns

    ):
        self.vacancies = DataSet(file_name=filename.strip())
        self.filter_parameter = self.get_filter(filter_parameter.strip())
        self.sort_parameter = sort_parameter.strip()
        self.is_revers = self.get_sort_way(is_revers.strip())
        self.print_range = print_range.strip().split(" ")
        self.print_columns = print_columns.strip().split(", ")
        self.filter_vacancies()

    def __str__(self):
        my_table = PrettyTable()
        row_count = 0
        my_table.field_names = [
            "№",
            "Название",
            "Описание",
            "Навыки",
            "Опыт работы",
            "Премиум-вакансия",
            "Компания",
            "Оклад",
            "Название региона",
            "Дата публикации вакансии"
        ]
        for row in self.vacancies.get_sorted(self.sort_parameter, self.is_revers):
            row_count += 1
            my_table.add_row([row_count.__str__()] + row.make_table_row())

        if row_count == 0:
            raise AssertionError

        self.format_table(my_table)

        if self.print_columns[0] == '':
            self.print_columns = my_table.field_names
        else:
            self.print_columns.insert(0, "№")
        if self.print_range[0] == '':
            self.print_range = [1, row_count + 1]
        elif len(self.print_range) < 2:
            self.print_range.append(str(row_count + 1))

        return my_table.get_string(
            fields=self.print_columns,
            start=int(self.print_range[0]) - 1,
            end=int(self.print_range[1]) - 1
        )

    @staticmethod
    def get_filter(string: str) -> tuple or None:
        filter_name_to_parse = {
            "key_skills": lambda to_parse:
            to_parse.split(", "),
            "salary": lambda to_parse:
            int(to_parse),
            "published_at": lambda to_parse:
            datetime.strptime(to_parse, "%d.%m.%Y"),
            "experience_id": lambda to_parse:
            Translator.inverse_dict(Translator.translation_experience)[to_parse],
            "premium": lambda to_parse:
            Translator.inverse_dict(Translator.translation_premium)[to_parse],
            "salary_currency": lambda to_parse:
            Translator.inverse_dict(Translator.translation_currency)[to_parse]
        }

        if string == '':
            return None
        if not string.__contains__(':'):
            raise IOError

        filter_rules = [x.strip() for x in string.split(':')]
        if not Translator.translation_filter.__contains__(filter_rules[0]):
            raise KeyError
        filter_name = Translator.translation_filter[filter_rules[0]]
        if filter_name_to_parse.__contains__(filter_name):
            filter_object = filter_name_to_parse[filter_name](filter_rules[1])
        else:
            filter_object = filter_rules[1]

        return filter_name, filter_object

    @staticmethod
    def get_sort_way(to_parse: str) -> bool:
        if to_parse == "Да":
            return True
        elif to_parse == "Нет" or to_parse == "":
            return False
        else:
            raise SortWayError

    def format_table(self, table: PrettyTable) -> None:
        table.hrules = 1
        table.max_width = 20
        table.min_width = 20
        table._min_width = {"№": 0}
        table.align = 'l'

    def filter_vacancies(self):
        filter_checker = {
            "key_skills": lambda vacancy:
            all(x in vacancy.key_skills for x in self.filter_parameter[1]),
            "salary": lambda vacancy:
            int(vacancy.salary.salary_from) <= self.filter_parameter[1] <= int(vacancy.salary.salary_to),
            "published_at": lambda vacancy:
            all([
                vacancy.published_at.year == self.filter_parameter[1].year,
                vacancy.published_at.month == self.filter_parameter[1].month,
                vacancy.published_at.day == self.filter_parameter[1].day
            ]),
            "experience_id": lambda vacancy:
            vacancy.experience_id == self.filter_parameter[1],
            "premium": lambda vacancy:
            vacancy.premium == self.filter_parameter[1],
            "salary_currency": lambda vacancy:
            vacancy.salary.salary_currency == self.filter_parameter[1],
            "name": lambda vacancy:
            vacancy.name == self.filter_parameter[1],
            "area_name": lambda vacancy:
            vacancy.area_name == self.filter_parameter[1],
            "employer_name": lambda vacancy:
            vacancy.employer_name == self.filter_parameter[1],
            "description": lambda vacancy:
            vacancy.description == self.filter_parameter[1]
        }

        if self.filter_parameter:
            self.vacancies.vacancies_reader = filter(
                filter_checker[self.filter_parameter[0]],
                self.vacancies.vacancies_reader
            )


try:
    input_connect = InputConnect(
        input("Введите название файла: "),
        input("Введите параметр фильтрации: "),
        input("Введите параметр сортировки: "),
        input("Обратный порядок сортировки (Да / Нет): "),
        input("Введите диапазон вывода: "),
        input("Введите требуемые столбцы: ")
    )
    print(input_connect)
except StopIteration:
    print("Пустой файл")
except IOError:
    print("Формат ввода некорректен")
except KeyError:
    print("Параметр поиска некорректен")
except SortParameterError:
    print("Параметр сортировки некорректен")
except SortWayError:
    print("Порядок сортировки задан некорректно")
except AssertionError:
    print("Ничего не найдено")
except OutOfDataError:
    print("Нет данных")
