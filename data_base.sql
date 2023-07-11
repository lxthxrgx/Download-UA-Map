CREATE TABLE IF NOT EXISTS public.info_about_cadnum
(
    id SERIAL PRIMARY KEY, 
    cadnum text COLLATE pg_catalog."default",
    category text COLLATE pg_catalog."default",
    area real COLLATE pg_catalog."default",
    unit_area text COLLATE pg_catalog."default",
    koatuu numeric COLLATE pg_catalog."default",
    use text COLLATE pg_catalog."default",
    purpose text COLLATE pg_catalog."default",
    purpose_code text COLLATE pg_catalog."default",
    ownership text COLLATE pg_catalog."default",
    ownershipcode numeric COLLATE pg_catalog."default",
    geom GEOMETRY(MultiPolygon,4326),
    address text COLLATE pg_catalog."default",
    valuation_value real COLLATE pg_catalog."default",
    valuation_date numeric COLLATE pg_catalog."default",
    geometry text COLLATE pg_catalog."default"
)

CREATE TABLE IF NOT EXISTS data_test
(
    id SERIAL PRIMARY KEY, 
    cadnum text COLLATE pg_catalog."default",
    category text COLLATE pg_catalog."default",
    area real COLLATE pg_catalog."default",
    unit_area text COLLATE pg_catalog."default",
    koatuu numeric COLLATE pg_catalog."default",
    use text COLLATE pg_catalog."default",
    purpose text COLLATE pg_catalog."default",
    purpose_code text COLLATE pg_catalog."default",
    ownership text COLLATE pg_catalog."default",
    ownershipcode numeric COLLATE pg_catalog."default",
    geom GEOMETRY(MultiPolygon,4326),
    address text COLLATE pg_catalog."default",
    valuation_value real COLLATE pg_catalog."default",
    valuation_date numeric COLLATE pg_catalog."default",
    geometry text COLLATE pg_catalog."default"
)


ALTER TABLE cadnum ADD CONSTRAINT unique_cad UNIQUE (cad);

CREATE TABLE cadnumtemp (cad TEXT);

CREATE TABLE cadnumerror (cader TEXT);
