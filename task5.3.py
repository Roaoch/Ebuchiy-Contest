import csv
import codecs
import re
from datetime import datetime
from typing import List, Generator, Dict


class OutOfDataError(BaseException):
    pass


class Translator:
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


class Salary:
    def __init__(self, salary_property: List[str]):
        self.salary_from = float(salary_property[0])
        self.salary_to = float(salary_property[1])
        if len(salary_property) == 4:
            self.salary_gross = salary_property[2]
            self.salary_currency = salary_property[3]
        else:
            self.salary_currency = salary_property[2]

    def get_salary(self) -> float:
        return (self.salary_from + self.salary_to) / 2 * Translator.currency_to_rub[self.salary_currency]


class Vacancy:
    def __init__(self, property_list: List[any], headline: List[str]):
        if len(headline) == 12:
            self.name = property_list[0]
            self.description = property_list[1]
            self.key_skills = property_list[2] if type(property_list[2]) == list else [property_list[2]]
            self.experience_id = property_list[3]
            self.premium = property_list[4]
            self.employer_name = property_list[5]
            self.salary = Salary(property_list[6:10])
            self.area_name = property_list[10]
            self.published_at = datetime.strptime(property_list[11], "%Y-%m-%dT%H:%M:%S%z")
        elif len(headline) == 6:
            self.name = property_list[0]
            self.salary = Salary(property_list[1:4])
            self.area_name = property_list[4]
            self.published_at = datetime.strptime(property_list[5], "%Y-%m-%dT%H:%M:%S%z")


class DataSet:
    __CLEANER = re.compile('<.*?>')
    __SPACE_CLEANER = re.compile('(\s\s+)|(\xa0)')

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.headline = []
        self.vacancies_reader = self.__clean_properties(
            vacancies=self.__reader(file_name=file_name)
        )

    def __reader(self, file_name: str) -> csv.reader:
        reader = csv.reader(codecs.open(file_name, "r", "utf_8_sig"), delimiter=',')
        self.headline = reader.__next__()
        return reader

    def __validate(self, element: List[str]) -> bool:
        if len(element) != len(self.headline):
            return False
        for i in range(len(element)):
            if element[i] == '':
                return False
        return True

    def __clean_properties(self, vacancies: csv.reader) -> Generator[Vacancy, None, None]:
        i = 0
        key_skills_index = self.headline.index("key_skills") if "key_skills_index" in self.headline else -1
        for vacancy in vacancies:
            i += 1
            clean_vacancy = []
            if self.__validate(element=vacancy):
                for merit_index in range(len(vacancy)):
                    if merit_index == key_skills_index:
                        temp_property = vacancy[merit_index].split('\n')
                        for i in range(len(temp_property)):
                            temp_property[i] = re.sub(self.__CLEANER, '', temp_property[i])
                            temp_property[i] = re.sub(self.__SPACE_CLEANER, ' ', temp_property[i]).strip()
                    else:
                        temp_property = re.sub(self.__CLEANER, '', vacancy[merit_index])
                        temp_property = re.sub(self.__SPACE_CLEANER, ' ', temp_property).strip()
                    clean_vacancy.append(temp_property)
                yield Vacancy(clean_vacancy, self.headline)
        if i == 0:
            raise OutOfDataError


class InputConnect:
    def __init__(
            self,
            filename,
            filter_parameter
    ):
        self.__vacancies = DataSet(file_name=filename.strip())
        self.__filter_parameter = filter_parameter.strip()
        self.all_salary_level = {}
        self.all_vacancies_count = {}
        self.salary_level = {}
        self.vacancies_count = {}
        self.by_city_level = {}
        self.vacancies_part = {}
        self.__get_statistics()

    def __get_statistics(self) -> None:
        temp_by_city_count = {}
        temp_by_city_level = {}
        temp_all_by_city_count = {}
        for vacancy in self.__vacancies.vacancies_reader:
            vacancy_year = vacancy.published_at.year
            vacancy_salary = vacancy.salary.get_salary()
            self.__add_to_or_update(
                self.all_salary_level,
                vacancy_year,
                vacancy_salary
            )
            self.__add_to_or_update(
                self.all_vacancies_count,
                vacancy_year,
                1
            )
            self.__add_to_or_update(
                temp_by_city_level,
                vacancy.area_name,
                vacancy_salary
            )
            self.__add_to_or_update(
                temp_all_by_city_count,
                vacancy.area_name,
                1
            )
            if self.__filter_parameter in vacancy.name:
                self.__add_to_or_update(
                    self.salary_level,
                    vacancy_year,
                    vacancy_salary
                )
                self.__add_to_or_update(
                    self.vacancies_count,
                    vacancy_year,
                    1
                )
                self.__add_to_or_update(
                    temp_by_city_count,
                    vacancy.area_name,
                    1
                )
        self.all_salary_level = {key: int(value / self.all_vacancies_count[key]) for key, value in self.all_salary_level.items()}
        self.salary_level = {key: int(value / self.vacancies_count[key]) for key, value in self.salary_level.items()}

        if len(self.salary_level) == 0:
            self.salary_level = {key: 0 for key in self.all_vacancies_count.keys()}
            self.vacancies_count = {key: 0 for key in self.all_vacancies_count.keys()}

        f = sum(temp_all_by_city_count.values())
        self.vacancies_part = dict(sorted(
            [(key, float("{:.4f}".format(value / f))) for key, value in temp_all_by_city_count.items() if value / f >= 0.01],
            key=lambda e: e[1],
            reverse=True
        ))
        self.by_city_level = dict(sorted(
            [(key, int(temp_by_city_level[key] / temp_all_by_city_count[key])) for key in self.vacancies_part.keys()],
            key=lambda e: (e[1], -len(e[0])),
            reverse=True
        ))

    def print_self(self) -> None:
        print(f"Динамика уровня зарплат по годам: {self.all_salary_level}")
        print(f"Динамика количества вакансий по годам: {self.all_vacancies_count}")
        print(f"Динамика уровня зарплат по годам для выбранной профессии: {self.salary_level}")
        print(f"Динамика количества вакансий по годам для выбранной профессии: {self.vacancies_count}")
        print(f"Уровень зарплат по городам (в порядке убывания): {self.__slice_dict(self.by_city_level, 10)}")
        print(f"Доля вакансий по городам (в порядке убывания): {self.__slice_dict(self.vacancies_part, 10)}")

    @staticmethod
    def __add_to_or_update(dictionary: Dict[any, any], key: any, value: any) -> None:
        if dictionary.__contains__(key):
            dictionary[key] += value
        else:
            dictionary.update({key: value})

    @staticmethod
    def __slice_dict(dictionary: dict, end: int):
        result = {}
        i = 0
        for key, value in dictionary.items():
            i += 1
            if i <= end:
                result.update({key: value})
            else:
                break
        return result


try:
    input_connect = InputConnect(
        input("Введите название файла: "),
        input("Введите название профессии: ")
    )
    input_connect.print_self()
except StopIteration:
    print("Пустой файл")
except IOError:
    print("Формат ввода некорректен")
except KeyError:
    print("Параметр поиска некорректен")
except AssertionError:
    print("Ничего не найдено")
except OutOfDataError:
    print("Нет данных")
