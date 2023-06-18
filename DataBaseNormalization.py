import re
import psycopg2

with open(r'practice\Downlaod UA Map\innertext1.txt', 'r', encoding='utf-8') as file:
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

database.commit()
cursor.close()
database.close()
