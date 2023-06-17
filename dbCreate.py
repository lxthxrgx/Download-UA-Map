import sqlite3 as sq

database = sq.connect('uamap.db')
cursor = database.cursor()

cursor.execute('''ALTER TABLE cadnum ADD CONSTRAINT unique_cad UNIQUE (cad);''')

cursor.execute("CREATE UNIQUE INDEX index_name ON table_name (column_name);")

cursor.execute('''CREATE TABLE IF NOT EXISTS public.cadnum
(
    cad text COLLATE pg_catalog."default",
    category text COLLATE pg_catalog."default",
    area text COLLATE pg_catalog."default",
    unit_area text COLLATE pg_catalog."default",
    koatuu text COLLATE pg_catalog."default",
    use text COLLATE pg_catalog."default",
    purpose text COLLATE pg_catalog."default",
    purpose_code text COLLATE pg_catalog."default",
    ownership text COLLATE pg_catalog."default",
    ownershipcode text COLLATE pg_catalog."default",
    geometry text COLLATE pg_catalog."default",
    address text COLLATE pg_catalog."default",
    valuation_value text COLLATE pg_catalog."default",
    valuation_date text COLLATE pg_catalog."default"
)
''')

cursor.execute('''CREATE TABLE cadnumtemp (cad TEXT);''')


database.commit()
database.close()