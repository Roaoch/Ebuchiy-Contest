#vacancies.csv
import csv
import codecs
import re


def validate(element, properties_count):
    is_valid = False
    if len(element) != properties_count:
        return False
    for i in range(len(element)):
        if element[i].replace(' ', '') == '':
            return False
    if not is_valid:
        return True


def make_dictionary(key, value):
    result = {}
    for i in range(len(key)):
        result.update({key[i]: value[i]})
    return result


CLEANER = re.compile('<.*?>')
SPACE_CLEANER = re.compile('(\s\s+)|(\xa0)')
def clean_properties(merits):
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


def increass_or_add(dictionary, key):
    dictionary.update({key: dictionary.get(key, 0) + 1})


file_name = input()
csv_reader = csv.reader(codecs.open(file_name, "r", "utf_8_sig"), delimiter=',')
head_line = csv_reader.__next__()
vacancies = []
vacancies_in_cities = {}
vacancies_count_in_cities = {}

for vacancy in csv_reader:
    if validate(vacancy, len(head_line)):
        dictionary = make_dictionary(head_line, clean_properties(vacancy))
        if dictionary["salary_currency"] == ["RUR"]:
            vacancies.append(dictionary)

            x = vacancies_in_cities.setdefault(dictionary["area_name"][0], {})
            increass_or_add(x, dictionary['name'][0])

            increass_or_add(vacancies_count_in_cities, dictionary["area_name"][0])
        # vacancies.append(dictionary)

for key in vacancies_count_in_cities.keys():
    temp = list(vacancies_in_cities[key].keys()).copy()
    for city_vacancy in temp:
        if vacancies_in_cities[key][city_vacancy] / vacancies_count_in_cities[key] <= 0.01:
            vacancies_in_cities[key].pop(city_vacancy)

# for vacancy in vacancies:
#     for vacancy_property in vacancy.keys():
#         print("%s: %s" % (vacancy_property, ", ".join(vacancy[vacancy_property]).strip(' ')))
#     print()
print(vacancies_in_cities)