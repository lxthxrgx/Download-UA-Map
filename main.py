import time
import json
import requests
from collections import OrderedDict
from termcolor import colored
import time
import concurrent.futures as cf
import os
import psycopg2
import proxyandheaders as proxy_h

def folder_check():

    folder_path = 'bf'

    if not os.path.exists(folder_path):
        print(colored('WARNINNG!!! folder does not exist', 'red'))
        time.sleep(1)
        print(colored('Creating folder...','yellow'))
        print(colored('Folder created!', 'green'))
        os.makedirs("bf")
    return len(os.listdir(folder_path)) == 0

cadnum_file = 'cadnum_data.txt'

proxy_dict = proxy_h.proxy_protocol_test()
headers_func = proxy_h.headers()

database = psycopg2.connect(
    host="localhost",
    database="kadastr",
    user="postgres",
    password="102030"
    )
cursor = database.cursor()

def db():
    start_y = 1149
    end_y = 1251

    start_x = 673-1
    end_x =  740    
    filenames = [f"bf/{y}-{x}.pbf" for y in range(start_y, end_y+1) for x in range(start_x,end_x)]
    with open("last_processed_file.txt", "r") as f:
        last_processed_filename = 'bf/' + f.read()

    try:
        if last_processed_filename is not None:
            filenames = filenames[filenames.index(last_processed_filename)-1:]
    except ValueError as ve:
       print(colored(ve,'red'))
    
    for filename in filenames:
        try:
            with open(filename, 'rb') as f:
                for line in f:
                    data_dict = json.loads(line)
                    features_list = data_dict["land_polygons"]["features"]
                    for feature in features_list:
                        data_d = feature['properties']['cadnum']
                        cursor.execute("INSERT INTO cadnumtemp (cad) VALUES (%s);", (data_d,))
                        database.commit() 
        except Exception :
            print(f'None Cadnum: {filename}')
        else:
            with open("last_processed_file.txt", "w") as f:
                f.write(os.path.basename(filename))
    database.close()   
 
request_count = 0


def download_info_cad(cad_data_f_db):
    global request_count
    data = None
    url = 'https://kadastr.live/api/parcels/' + str(cad_data_f_db) + '/history/?format=json'
    try:
        response = requests.get(url)
        request_count += 1
        if response.status_code == 200:
            data = response.json()
            print('Количество выполненных запросов:', request_count)
            save_data_to_db(data)  # Сохранение данных в базу данных сразу после получения ответа
        else:
            print('Ошибка получения JSON-данных:', response.status_code, url)
    except Exception:
        database = psycopg2.connect(
        host="localhost",
        database="kadastr",
        user="postgres",
        password="102030"
        )
        cursor = database.cursor()
        cursor.execute('INSERT INTO cadnumerror(cader) VALUES(%s);', (cad_data_f_db,))
        database.close()
    return data



def save_data_to_db(data_filtered):
    database = psycopg2.connect(
    host="localhost",
    database="kadastr",
    user="postgres",
    password="102030")

    cursor = database.cursor()

    if data_filtered is not None:
        a = data_filtered['geometry']['coordinates']
        string_a = ' , '.join(map(str, a))
        cursor.execute('''INSERT INTO cadnum (
            cad,
            category,
            area,
            unit_area,
            koatuu,
            use,
            purpose,
           purpose_code,
           ownership,
            ownershipcode,
           geometry,
            address,
            valuation_value,
            valuation_date
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);''',
            (data_filtered['cadnum'], data_filtered['category'], data_filtered['area'], data_filtered['unit_area'], data_filtered['koatuu'], data_filtered['use'], data_filtered['purpose'], data_filtered['purpose_code'], data_filtered['ownership'], data_filtered['ownershipcode'], string_a, data_filtered['address'], data_filtered['valuation_value'], data_filtered['valuation_date']))
    database.commit()
    database.close()

max_threads = 5

database = psycopg2.connect(
    host="localhost",
    database="kadastr",
    user="postgres",
    password="102030"
    )
cursor = database.cursor()

cursor.execute("SELECT cad FROM cadnumtemp ")
column_data_temp = cursor.fetchall()
cleaned_db_column_data_cad = [item[0].replace('(', '').replace(')', '').replace(',', '') if item[0] is not None else '' for item in column_data_temp]
database.close()

with cf.ThreadPoolExecutor(max_workers=max_threads) as executor:
    results = [executor.submit(download_info_cad, cad_data) for cad_data in cleaned_db_column_data_cad]

counter = 0

for future in cf.as_completed(results):
    data_filtered = future.result()
    counter += 1
    if counter % 100000 == 0:
        print('Процесс сохранения данных в базу данных:', counter)