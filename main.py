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
import threading
import time
from psycopg2.extras import Json
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
lock = threading.RLock()

def db():
    start_y = 1149
    start_x = 673-1
    end_y = 1251
    end_x =  740  
    filenames = [f"bf/{y}-{x}.pbf" for y in range(start_y, end_y+1) for x in range(start_x,end_x)]
    with open("last_processed_file.txt", "r") as f:
        last_processed_filename = 'bf/' + f.read()
    try:
        if last_processed_filename is not None:
            filenames = filenames[filenames.index(last_processed_filename)-1:]
    except ValueError as ve:
       print(colored(ve,'red'))
    with psycopg2.connect(host="localhost", database="uamap", user="postgres", password="102030") as database:
        with database.cursor() as cursor:
            for filename in filenames:
                try:
                    with open(filename, 'rb') as f:
                        for line in f:
                            data_dict = json.loads(line)
                            features_list = data_dict["land_polygons"]["features"]
                            for feature in features_list:
                                data_d = feature['properties']['cadnum']
                                cursor.execute("INSERT INTO cadnum_data (cadnum) VALUES (%s);", (data_d,))
                                database.commit() 
                except Exception :
                    print(f'None Cadnum: {filename}')
                else:
                    with open("last_processed_file.txt", "w") as f:
                        f.write(os.path.basename(filename))
    cursor.close()                    
    database.close()    

def download_info_cad(cad_data_f_db, cursor, database):
    start = time.time()
    with lock:
        try:
            data = None
            url = 'https://kadastr.live/api/parcels/' + str(cad_data_f_db) + '/history/?format=json'
            try:   
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    save_data_to_db(data, cursor, database)
                else:
                    print('Ошибка получения JSON-данных:', response.status_code, url)
            except Exception:
                    cursor.execute('INSERT INTO error_cadnum_info(cadnum_error) VALUES(%s);', (cad_data_f_db,))
                    database.commit()
        except Exception as e:
            print('Ошибка подключения к базе данных:', str(e))
    end = time.time()
    execution = end - start
    print("Время выполнения download_info_cad:", execution, "секунд", 'Url:', url)

def save_data_to_db(data_filtered, cursor, database):
    start = time.time()
    try:
        if data_filtered is not None:
            with lock:
                cursor.execute(
                    '''INSERT INTO info_about_cadnum (
                        cadnum,
                        category,
                        area,
                        unit_area,
                        koatuu,
                        use,
                        purpose,
                        purpose_code,
                        ownership,
                        ownershipcode,
                        geom,
                        address,
                        valuation_value,
                        valuation_date,
                        geometry
                        ) 
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), 
                            %s, %s, %s, %s
                        );''',
                            (
                                data_filtered['cadnum'], data_filtered['category'], data_filtered['area'], data_filtered['unit_area'], 
                                data_filtered['koatuu'], data_filtered['use'], data_filtered['purpose'], data_filtered['purpose_code'], 
                                data_filtered['ownership'], data_filtered['ownershipcode'], Json(data_filtered['geometry']), data_filtered['address'], 
                                data_filtered['valuation_value'], data_filtered['valuation_date'], Json(data_filtered['geometry'])
                            )
                    )

                database.commit()
    except Exception as e:
        print('Ошибка сохранения данных в базу данных:', cursor.execute('INSERT INTO error_cadnum_info(cadnum_error) VALUES(%s);', (data_filtered['cadnum'],)))
        print(e)
    end = time.time()
    execution = end - start
    if execution == 0:
        print("Время выполнения save_data_to_db:", colored(execution,'red'), "секунд")
    else:
        print("Время выполнения save_data_to_db:", colored(execution,'green'), "секунд")


max_threads = 10

with psycopg2.connect(host="localhost", database="uamap", user="postgres", password="102030") as database:
    with database.cursor() as cursor:

        cursor.execute("SELECT cadnum FROM cadnum_data LIMIT 1000000 OFFSET 174247")
        column_data_temp = cursor.fetchall()
        cleaned_db_column_data_cad = [item[0].replace('(', '').replace(')', '').replace(',', '') if item[0] is not None else '' for item in column_data_temp]

        try:
            with cf.ThreadPoolExecutor(max_workers=max_threads) as executor:
                results = []
                for cad_data in cleaned_db_column_data_cad:
                    future = executor.submit(download_info_cad, cad_data, cursor, database)
                    results.append(future)

                #for future in cf.as_completed(results):
                    #try:
                        #data_filtered = future.result()
                        #save_data_to_db(data_filtered, cursor, database)
                    #except Exception as e:
                        #print('Ошибка выполнения функции:', str(e))
        except Exception as e:
            print('Ошибка подключения к базе данных:', str(e))
cursor.close()
database.close()
