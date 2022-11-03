import csv
import codecs
import re
from var_dump import var_dump
from typing import List


class Salary:
    def __init__(self, salary_property: List[str]):
        self.salary_from = salary_property[1]
        self.salary_to = salary_property[2]
        self.salary_gross = salary_property[3]
        self.salary_currency = salary_property[4]


class Vacancy:
    def __init__(self, property_list: List[any]):
        self.name = property_list[0]
        self.description = property_list[1]
        self.key_skills = property_list[2]
        self.experience_id = property_list[3]
        self.premium = property_list[4]
        self.employer_name = property_list[5]
        self.salary = Salary(property_list[5:10])
        self.area_name = property_list[10]
        self.published_at = property_list[11]


class DataSet:
    __CLEANER = re.compile('<.*?>')
    __SPACE_CLEANER = re.compile('(\s\s+)|(\xa0)')

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.vacancies_objects = self.__clean_properties(
            vacancies=self.__reader(file_name=file_name)
        )

    @staticmethod
    def __reader(file_name: str) -> csv.reader:
        reader = csv.reader(codecs.open(file_name, "r", "utf_8_sig"), delimiter=',')
        reader.__next__()
        return reader

    @staticmethod
    def __validate(element: List[str]) -> bool:
        if len(element) == 0:
            return False
        for i in range(len(element)):
            if element[i].replace(' ', '') == '':
                return False
        return True

    def __clean_properties(self, vacancies: csv.reader) -> List[Vacancy]:
        result = []
        for vacancy in vacancies:
            clean_vacancy = []
            if self.__validate(element=vacancy):
                for merit in vacancy:
                    temp_property = merit.replace("\r\n", '\n').split('\n')
                    if len(temp_property) > 1:
                        for i in range(len(temp_property)):
                            temp_property[i] = re.sub(self.__CLEANER, '', temp_property[i])
                            temp_property[i] = re.sub(self.__SPACE_CLEANER, ' ', temp_property[i]).strip()
                    else:
                        temp_property = re.sub(self.__CLEANER, '', temp_property[0])
                        temp_property = re.sub(self.__SPACE_CLEANER, ' ', temp_property).strip()
                    clean_vacancy.append(temp_property)
                result.append(Vacancy(clean_vacancy))
        return result


class InputConnect:
    def __init__(self):
        self.file_name = input("Введите название файла: ")
        self.filter_parameter = input("Введите параметр фильтрации: ")
        self.sort_parameter = input("Введите параметр сортировки: ")
        self.is_revers = input("Обратный порядок сортировки (Да / Нет): ")
        self.print_range = input("Введите диапазон вывода: ")
        self.print_columns = input("Введите требуемые столбцы: ")


input_connect = InputConnect()
try:
    var_dump(DataSet(input_connect.file_name).vacancies_objects)
except StopIteration:
    print("Пустой файл")
