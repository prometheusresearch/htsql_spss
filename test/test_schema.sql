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

ALTER TABLE ONLY individual
    ADD CONSTRAINT individual_pk PRIMARY KEY (code);
ALTER TABLE individual CLUSTER ON individual_pk;
ALTER TABLE ONLY individual
    ADD CONSTRAINT individual_uk UNIQUE (id);

ALTER TABLE ONLY sample_type
    ADD CONSTRAINT sample_type__pk PRIMARY KEY (code);
ALTER TABLE sample_type CLUSTER ON sample_type__pk;
ALTER TABLE ONLY sample_type
    ADD CONSTRAINT sample_type__uk UNIQUE (id);

ALTER TABLE ONLY sample
    ADD CONSTRAINT sample_pk PRIMARY KEY (individual_id, sample_type__id, code);
ALTER TABLE sample CLUSTER ON sample_pk;
ALTER TABLE ONLY sample
    ADD CONSTRAINT sample_uk UNIQUE (id);

ALTER TABLE ONLY tube
    ADD CONSTRAINT tube_pk PRIMARY KEY (sample_id, code);
ALTER TABLE tube CLUSTER ON tube_pk;
ALTER TABLE ONLY tube
    ADD CONSTRAINT tube_uk UNIQUE (id);

CREATE INDEX sample__sample_type__fk ON sample USING btree (sample_type__id);
CREATE INDEX sample_individual_fk ON sample USING btree (individual_id);
CREATE INDEX tube_sample_fk ON tube USING btree (sample_id);

ALTER TABLE ONLY sample
    ADD CONSTRAINT sample_individual_fk FOREIGN KEY (individual_id) REFERENCES individual(id) ON DELETE CASCADE;
ALTER TABLE ONLY sample
    ADD CONSTRAINT sample__sample_type__fk FOREIGN KEY (sample_type__id) REFERENCES sample_type(id) ON DELETE CASCADE;
ALTER TABLE ONLY tube
    ADD CONSTRAINT tube_sample_fk FOREIGN KEY (sample_id) REFERENCES sample(id) ON DELETE CASCADE;

