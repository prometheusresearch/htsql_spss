CREATE SCHEMA spss;

CREATE TABLE individual (
    id integer NOT NULL,
    code text NOT NULL
);

CREATE TABLE sample_type (
    id integer NOT NULL,
    code text NOT NULL,
    title text NOT NULL
);

CREATE TABLE sample (
    id integer NOT NULL,
    sample_type__id integer NOT NULL,
    individual_id integer NOT NULL,
    code integer NOT NULL,
    contaminated boolean NOT NULL,
    date_collected date,
    time_collected time without time zone,
    date_time_collected timestamp without time zone
);

CREATE TYPE tube__volume_unit__enum AS ENUM (
    'ml',
    'ul'
);

CREATE TABLE tube (
    id integer NOT NULL,
    sample_id integer NOT NULL,
    code integer NOT NULL,
    volume_amount numeric,
    volume_unit tube__volume_unit__enum,
    location_memo text
);
