
CREATE TABLE IF NOT EXISTS public.cadnum
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

CREATE TABLE cadnumtemp (cad TEXT);

CREATE TABLE cadnumerror (cader TEXT);

ALTER TABLE cadnum ADD CONSTRAINT unique_cad UNIQUE (cad);
CREATE TABLE IF NOT EXISTS public.normalized_purpose
(
    purpose text COLLATE pg_catalog."default",
    norm_purpose text COLLATE pg_catalog."default"
)
