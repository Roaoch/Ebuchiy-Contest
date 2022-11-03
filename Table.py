import csv
import codecs
import re
import enum
from datetime import datetime
from typing import Generator


file = input("Введите название файла: ")


class SortParameterError(BaseException):
    pass


class SortWayError(BaseException):
    pass


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


try:
    def vacancy_parser(func):
        from prettytable import PrettyTable

        def get_filter(string: str) -> tuple or None:
            if string == '':
                return None
            if not string.__contains__(':'):
                raise IOError
            filter_rules = [x.strip() for x in string.split(':')]
            if not translation_filter.__contains__(filter_rules[0]):
                raise KeyError
            filter_name = translation_filter[filter_rules[0]]
            if filter_name_to_parse.__contains__(filter_name):
                filter_object = filter_name_to_parse[filter_name](filter_rules[1])
            else:
                filter_object = filter_rules[1]

            return filter_name, filter_object

        def validate_sorter(string: str) -> None:
            if not translation_filter.__contains__(string) and string != "":
                raise SortParameterError

        def parse_to_bool(string: str):
            if string != "Да" and string != "Нет" and string != "":
                raise SortWayError
            return True if string == "Да" else False

        def inverse_dict(straight: dict) -> dict:
            return {v: k for k, v in straight.items()}

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
        translation_premium = {
            "False": "Нет",
            "True": "Да"
        }
        translation_gross = {
            "False": "С вычетом налогов",
            "True": "Без вычета налогов"
        }
        translation_filter = {
            "Навыки": HeadKey.key_skills,
            "Оклад": HeadKey.salary,
            "Дата публикации вакансии": HeadKey.published_at,
            "Опыт работы": HeadKey.experience_id,
            "Премиум-вакансия": HeadKey.premium,
            "Идентификатор валюты оклада": HeadKey.salary_currency,
            "Название": HeadKey.name,
            "Название региона": HeadKey.area_name,
            "Компания": HeadKey.employer_name,
            "Описание": HeadKey.description
        }
        filter_name_to_parse = {
            HeadKey.key_skills: lambda to_parse: to_parse.split(", "),
            HeadKey.salary: lambda to_parse: int(to_parse),
            HeadKey.published_at: lambda to_parse: datetime.strptime(to_parse, "%d.%m.%Y"),
            HeadKey.experience_id: lambda to_parse: inverse_dict(translation_experience)[to_parse],
            HeadKey.premium: lambda to_parse: inverse_dict(translation_premium)[to_parse],
            HeadKey.salary_currency: lambda to_parse: inverse_dict(translation_currency)[to_parse]
        }
        filter_checker = {
            HeadKey.key_skills: lambda vacancy, filter_key:
            all(x in vacancy[HeadKey.key_skills] for x in filter_key),
            HeadKey.salary: lambda vacancy, filter_key:
            int(vacancy[HeadKey.salary_from][0]) <= filter_key <= int(vacancy[HeadKey.salary_to][0]),
            HeadKey.published_at: lambda vacancy, filter_key:
            are_equal(vacancy[HeadKey.published_at][0], filter_key),
            HeadKey.experience_id: lambda vacancy, filter_key:
            vacancy[HeadKey.experience_id][0] == filter_key,
            HeadKey.premium: lambda vacancy, filter_key:
            vacancy[HeadKey.premium][0] == filter_key,
            HeadKey.salary_currency: lambda vacancy, filter_key:
            vacancy[HeadKey.salary_currency][0] == filter_key,
            HeadKey.name: lambda vacancy, filter_key:
            vacancy[HeadKey.name][0] == filter_key,
            HeadKey.area_name: lambda vacancy, filter_key:
            vacancy[HeadKey.area_name][0] == filter_key,
            HeadKey.employer_name: lambda vacancy, filter_key:
            vacancy[HeadKey.employer_name][0] == filter_key,
            HeadKey.description: lambda vacancy, filter_key:
            vacancy[HeadKey.description][0] == filter_key
        }
        formatter_row = {
            lambda row: row.__setitem__(HeadKey.description,
                                        [row[HeadKey.description][0].strip()]),
            lambda row: row.__setitem__(HeadKey.key_skills,
                                        ["\n".join(row[HeadKey.key_skills])]),
            lambda row: row.__setitem__(HeadKey.premium,
                                        [translation_premium[row[HeadKey.premium][0].capitalize()]]),
            lambda row: row.__setitem__(HeadKey.experience_id,
                                        [translation_experience[row[HeadKey.experience_id][0]]]),
            lambda row: row.__setitem__(HeadKey.published_at,
                                        [datetime.strftime(row[HeadKey.published_at][0], "%d.%m.%Y")])
        }
        sorter = {
            HeadKey.key_skills: lambda to_sort:
                len(to_sort[HeadKey.key_skills]),
            HeadKey.salary: lambda to_sort:
                (float(to_sort[HeadKey.salary_from][0]) + float(to_sort[HeadKey.salary_to][0]))
                / 2 * currency_to_rub[to_sort[HeadKey.salary_currency][0]],
            HeadKey.published_at: lambda to_sort:
                to_sort[HeadKey.published_at][0],
            HeadKey.experience_id: lambda to_sort:
                experience_to_int[to_sort[HeadKey.experience_id][0]],
            HeadKey.premium: lambda to_sort:
                to_sort[HeadKey.premium][0],
            HeadKey.name: lambda to_sort:
                to_sort[HeadKey.name][0],
            HeadKey.area_name: lambda to_sort:
                to_sort[HeadKey.area_name][0],
            HeadKey.employer_name: lambda to_sort:
                to_sort[HeadKey.employer_name][0],
            HeadKey.description: lambda to_sort:
                to_sort[HeadKey.description][0]
        }

        filter_parameter = input("Введите параметр фильтрации: ")
        sorter_parameter = input("Введите параметр сортировки: ").strip()
        is_sort_reversed = input("Обратный порядок сортировки (Да / Нет): ")
        print_range = input("Введите диапазон вывода: ")
        print_columns = input("Введите требуемые столбцы: ")

        validate_sorter(sorter_parameter)
        filter_parameter = get_filter(filter_parameter.strip())
        is_sort_reversed = parse_to_bool(is_sort_reversed.strip())
        print_range = print_range.strip().split(" ")
        print_columns = print_columns.strip().split(", ")

        def vacancy_sort(to_sort: list, sort_by: str, is_reverse: bool) -> list:
            if sort_by != "":
                sort_by = translation_filter[sort_by]
                to_sort.sort(key=sorter[sort_by], reverse=is_reverse)
            return to_sort

        def format_table(table: PrettyTable) -> None:
            table.hrules = 1
            table.field_names = [
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
            table.max_width = 20
            table.min_width = 20
            table._min_width = {"№": 0}
            table.align = 'l'

        def formatter(row: dict) -> list:
            for function in formatter_row:
                function(row)

            return list(make_table_row(make_salary(row)))

        def make_table_row(row: dict) -> list:
            for row_value in row.values():
                row_value = row_value[0]
                if len(row_value) > 100:
                    row_value = row_value[:100] + "..."
                yield row_value

        def are_equal(first: datetime, second: datetime) -> bool:
            return all([
                first.year == second.year,
                first.month == second.month,
                first.day == second.day
            ])

        def format_float(salary: str) -> str:
            return "{:,.0f}".format(float(salary)).replace(',', ' ')

        def get_salary(vacancy: dict) -> str:
            salary = "{0} - {1} ({2}) ({3})".format(
                format_float(vacancy[HeadKey.salary_from][0]),
                format_float(vacancy[HeadKey.salary_to][0]),
                translation_currency[vacancy[HeadKey.salary_currency][0]],
                translation_gross[vacancy[HeadKey.salary_gross][0]]
            )
            return salary

        def make_salary(dictionary: dict) -> dict:
            dictionary_as_list = list(dictionary.items())
            dictionary_as_list.insert(6, (HeadKey.salary, [get_salary(dictionary)]))
            dictionary = dict(dictionary_as_list)
            del dictionary[HeadKey.salary_from]
            del dictionary[HeadKey.salary_to]
            del dictionary[HeadKey.salary_gross]
            del dictionary[HeadKey.salary_currency]

            return dictionary

        def print_vacancies(data_vacancies: list) -> None:
            my_table = PrettyTable()
            row_count = 0
            nonlocal print_columns
            nonlocal print_range

            for row in data_vacancies:
                row_count += 1
                my_table.add_row([row_count] + formatter(row))

            if row_count == 0:
                raise AssertionError

            format_table(my_table)
            if print_columns[0] == '':
                print_columns = my_table.field_names
            else:
                print_columns.insert(0, "№")

            if print_range[0] == '':
                print_range = [1, row_count + 1]
            elif len(print_range) < 2:
                print_range.append(str(row_count + 1))

            print_range = [int(x) for x in print_range]
            print(my_table.get_string(
                fields=print_columns,
                start=print_range[0] - 1,
                end=print_range[1] - 1
            ))

        def wrapper(*args):
            vacancies = []
            for vacancy in func(*args):
                if (not filter_parameter) or \
                        (not filter_checker.__contains__(filter_parameter[0]) and
                         vacancy[filter_parameter[0]][0] == filter_parameter[1]) or \
                        (filter_checker[filter_parameter[0]](vacancy, filter_parameter[1])):
                    vacancies.append(vacancy)

            print_vacancies(vacancy_sort(vacancies, sorter_parameter, is_sort_reversed))
            return vacancies

        return wrapper


    class CsvParser:
        __CLEANER = re.compile('<.*?>')
        __SPACE_CLEANER = re.compile('(\s\s+)|(\xa0)')

        @staticmethod
        def parse_to_bool(string: str):
            return True if string == "Да" else False

        @staticmethod
        def __reader(file_name: str) -> list:
            reader = csv.reader(codecs.open(file_name, "r", "utf_8_sig"), delimiter=',')
            reader.__next__()
            return list(reader)

        @staticmethod
        def __make_dictionary(keys: list, values: list) -> dict:
            keys = list(map(lambda x: HeadKey.__getitem__(x), keys))
            result = dict(zip(keys, values))
            result[HeadKey.published_at] = [datetime.strptime(
                result[HeadKey.published_at][0],
                "%Y-%m-%dT%H:%M:%S%z"
            )]
            result[HeadKey.published_at][0] = result[HeadKey.published_at][0].replace(tzinfo=None)
            return result

        @staticmethod
        def __validate(element: list, properties_count: int) -> bool:
            if len(element) != properties_count - 1:
                return False
            for i in range(len(element)):
                if element[i].replace(' ', '') == '':
                    return False
            return True

        def __clean_properties(self, merits: list) -> list:
            result = []
            for merit in merits:
                temp_property = merit.replace("\r\n", '\n')
                temp_property = temp_property.split('\n')
                for i in range(len(temp_property)):
                    temp_property[i] = re.sub(self.__CLEANER, '', temp_property[i])
                    temp_property[i] = re.sub(self.__SPACE_CLEANER, ' ', temp_property[i])
                result.append(temp_property)
            return result

        def __csv_filer(self, reader: list, list_naming: list) -> Generator[dict, None, None]:
            for line in reader:
                if self.__validate(line, len(list_naming)):
                    yield self.__make_dictionary(list_naming, self.__clean_properties(line))

        @vacancy_parser
        def csv_parse(self, file_name):
            data = self.__reader(file_name)
            if len(data) == 0:
                raise Exception
            return self.__csv_filer(data, list(HeadKey.__members__))


    csv_parser = CsvParser()
    csv_parser.csv_parse(file)

except StopIteration:
    print("Пустой файл")
except IOError:
    print("Формат ввода некорректен")
except KeyError:
    print("Параметр поиска некорректен")
except AssertionError:
    print("Ничего не найдено")
except SortParameterError:
    print("Параметр сортировки некорректен")
except SortWayError:
    print("Порядок сортировки задан некорректно")
# except Exception:
#     print("Нет данных")
