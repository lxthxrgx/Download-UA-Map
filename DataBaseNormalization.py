import re
import psycopg2

with open(r'F:\Prog\Py\practice\Downlaod UA Map\innertext1.txt', 'r', encoding='utf-8') as file:
   lines = file.readlines()

filter_file = r'[+]?\d{2}\.\d{2}'
normalized_data_from_file_list = re.findall(filter_file, ''.join(lines))
normalized_data_from_file_list = list(set(normalized_data_from_file_list))

for number in normalized_data_from_file_list:
    if float(number) <= 19 and float(number) != 12.11:
       float_normalized_data_from_file_list = float(number) 

key = 'Для'
result = None

for line in lines:
    if key in line:
        result = line.strip()
    print(result)
file.close()
with psycopg2.connect(host="localhost", database="kadastr", user="postgres", password="102030") as database:
    with database.cursor() as cursor:

        cursor.execute('CREATE TABLE IF NOT EXISTS normalized_purpose(purpose TEXT ,purpose_info TEXT, norm_purpose TEXT )')
        #cursor.execute('ALTER TABLE normalized_purpose ADD CONSTRAINT unique_purpose UNIQUE (purpose);')

        for numbers in float_normalized_data_from_file_list:
            cursor.execute('INSERT INTO normalized_purpose (purpose) VALUES(%s);', (numbers,))

        cursor.execute('SELECT purpose FROM cadnum')
        rows = cursor.fetchall()
       
        for row in rows:
            value = row[0]
            cursor.execute('INSERT INTO normalized_purpose(norm_purpose) VALUES(%s);', (value,))

def find_string(file_name, start_string, end_string):
    purpose_list = []
    with open(file_name, 'r', encoding='utf-8') as file:
        found_start = False
        found_end = False
        for line in file:
            if start_string in line:
                found_start = True
            if found_start and end_string in line:
                found_end = True
                break
            if found_start and not found_end:
                stripped_line = line.strip()
                if stripped_line not in purpose_list:
                    purpose_list.append(stripped_line)
    return purpose_list

file_name = 'F:\Prog\Py\practice\Downlaod UA Map\innertext1.txt'
start_string = '01.01'
end_string = '{Класифікація із змінами, внесеними згідно з Наказом Міністерства аграрної політики та продовольства № 587 від 28.09.2012, Наказом Міністерства регіонального розвитку, будівництва та житлово-комунального господарства № 287 від 12.11.2015, Наказом Міністерства аграрної політики та продовольства № 261 від 23.05.2017}'
for i in find_string(file_name, start_string, end_string):
    print(i)

database.commit()
cursor.close()
database.close()
