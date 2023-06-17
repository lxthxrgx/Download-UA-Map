import io
import re
import psycopg2

reader = io.open(r'practice\Downlaod UA Map\innertext1.txt', 'r', encoding='utf-8')
text = reader.read()
filter_file = r'[+]?\d{2}\.\d{2}'

normalized_data_from_file_list = re.findall(filter_file, text)

normalized_data_from_file_list = list(dict.fromkeys(normalized_data_from_file_list))

result = ''.join(normalized_data_from_file_list)
#
float_normalized_data_from_file_list = []
for number in normalized_data_from_file_list:
    float_number = float(number)
    if float_number <= 19:
        if float_number != 12.11:
            float_normalized_data_from_file_list.append(float_number)

with psycopg2.connect(host="localhost", database="kadastr", user="postgres", password="102030") as database:
    with database.cursor() as cursor:
        cursor.execute('CREATE TABLE IF NOT EXISTS normalized_purpose(purpose TEXT ,norm_purpose TEXT )')
        #cursor.execute('ALTER TABLE normalized_purpose ADD CONSTRAINT unique_purpose UNIQUE (purpose);')
        for numbers in float_normalized_data_from_file_list:
            cursor.execute('INSERT INTO normalized_purpose (purpose) VALUES(%s);', (numbers,))
        cursor.execute('SELECT purpose FROM cadnum')
        rows = cursor.fetchall()
        for row in rows:
            value = row[0]
            cursor.execute('INSERT INTO normalized_purpose(norm_purpose) VALUES(%s);', (value,))
#peredelat'
database.commit()
cursor.close()
database.close()    