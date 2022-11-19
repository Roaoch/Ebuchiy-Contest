import csv

with open(input(), newline='') as csvfile:
    for i in csv.reader(csvfile, delimiter=","):
        print(i)