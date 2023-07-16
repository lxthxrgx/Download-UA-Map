import json
import requests
import concurrent.futures as cf
import os
import psycopg2
import settings as settings
def folder_check():

    folder_path = 'bf'

    if not os.path.exists(folder_path):
        os.makedirs("bf")
    return len(os.listdir(folder_path)) == 0

#proxy_dict = proxy_h.proxy_protocol_test()
#headers_func = proxy_h.headers()

def db():
    settings.start_x
    settings.start_y
    settings.end_x
    settings.end_y
    filenames = [f"bf/{y}-{x}.pbf" for y in range(settings.start_y, settings.end_y+1) for x in range(settings.start_x,settings.end_x)]
    with open("last_processed_file.txt", "r") as f:
        last_processed_filename = 'bf/' + f.read()
    try:
        if last_processed_filename is not None:
            filenames = filenames[filenames.index(last_processed_filename)-1:]
    except ValueError as ve:
       print(ve)
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
        try:
            data = None
            url = 'https://kadastr.live/api/parcels/' + str(cad_data_f_db) + '/history/?format=json'
            try:   
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    save_data_to_db(data, cursor, database)
                else:
                    print('Ошибка получения JSON-данных:', response.status_code, url), cursor.execute('INSERT INTO error_cadnum_info(cadnum_error) VALUES(%s);', (cad_data_f_db,))
            except Exception:
                    cursor.execute('INSERT INTO error_cadnum_info(cadnum_error) VALUES(%s);', (cad_data_f_db,))
                    database.commit()
        except Exception as e:
            print('Ошибка подключения к базе данных:', str(e))

def save_data_to_db(data_filtered, cursor, database):
    try:
        if data_filtered is not None:
            string_my = json.dumps(data_filtered['geometry'])
            cursor.execute(
                    '''INSERT INTO data_test (
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
                        address,
                        valuation_value,
                        valuation_date,
                        geometry
                        ) 
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        );''',
                            (
                                data_filtered['cadnum'], data_filtered['category'], data_filtered['area'], data_filtered['unit_area'], 
                                data_filtered['koatuu'], data_filtered['use'], data_filtered['purpose'], data_filtered['purpose_code'], 
                                data_filtered['ownership'], data_filtered['ownershipcode'], data_filtered['address'], 
                                data_filtered['valuation_value'], data_filtered['valuation_date'], string_my,
                            )
                            )
            database.commit()
    except Exception as e:
        print('Ошибка сохранения данных в базу данных:', cursor.execute('INSERT INTO error_cadnum_info(cadnum_error) VALUES(%s);', (data_filtered['cadnum'],)))
        print(e) 

max_threads = 20

with psycopg2.connect(host="localhost", database="uamap", user="postgres", password="102030") as database:
    with database.cursor() as cursor:

        cursor.execute("SELECT cadnum FROM cadnum_data LIMIT 500000 OFFSET 1335469")
        column_data_temp = cursor.fetchall()
        cleaned_db_column_data_cad = [item[0].replace('(', '').replace(')', '').replace(',', '') if item[0] is not None else '' for item in column_data_temp]
        try:
            with cf.ThreadPoolExecutor(max_workers=max_threads) as executor:
                results = []
                for cad_data in cleaned_db_column_data_cad:
                    future = executor.submit(download_info_cad, cad_data, cursor, database)
                    results.append(future)
        except Exception as e:
            print('Ошибка подключения к базе данных:', str(e))
cursor.close()
database.close()
