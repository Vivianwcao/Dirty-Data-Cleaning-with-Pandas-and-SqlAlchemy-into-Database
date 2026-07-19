CREATE TABLE perfume_brands(
    id int generated always AS identity PRIMARY KEY,
    brand varchar(150)
);

CREATE TABLE perfume_types(
    id int generated always AS identity PRIMARY KEY,
    TYPE varchar(150)
);

CREATE TABLE staging_perfumes(
    staging_id int,
    brand varchar(150),
    TYPE varchar(150),
    title varchar(200),
    price numeric(12, 2),
    available int,
    sold int,
    last_updated timestamptz,
    item_location varchar(200),
    currency varchar(20),
    sex varchar(10),
    address varchar(200),
    country varchar(50),
    invalid_address bool
);

CREATE TABLE perfumes(
    id int generated always AS identity PRIMARY KEY,
    staging_id int,
    -- temporary!
    brand_id int,
    title varchar(200),
    price numeric(12, 2),
    available int,
    sold int,
    last_updated timestamptz,
    item_location varchar(200),
    currency varchar(20),
    sex varchar(10),
    address varchar(200),
    country varchar(50),
    invalid_address bool,
    FOREIGN KEY (brand_id) REFERENCES perfume_brands(id) ON DELETE
    SET
        NULL
);

--staging junction table
CREATE TABLE staging_perfume_types_junction(staging_id int, TYPE varchar(150));

--junction table
CREATE TABLE perfume_types_junction(
    id int generated always AS identity PRIMARY KEY,
    perfume_id int,
    type_id int,
    FOREIGN KEY (perfume_id) REFERENCES perfumes(id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES perfume_types(id) ON DELETE CASCADE
);

INSERT INTO
    perfumes (
        staging_id,
        brand_id,
        title,
        price,
        available,
        sold,
        last_updated,
        item_location,
        currency,
        sex,
        address,
        country,
        invalid_address
    )
SELECT
    sp.staging_id,
    pb.id,
    sp.title,
    sp.price,
    sp.available,
    sp.sold,
    sp.last_updated,
    sp.item_location,
    sp.currency,
    sp.sex,
    sp.address,
    sp.country,
    sp.invalid_address
FROM
    staging_perfumes sp
    LEFT JOIN perfume_brands pb ON sp.brand = pb.brand;

INSERT INTO
    perfume_types_junction (perfume_id, type_id)
SELECT
    p.id,
    pt.id
FROM
    staging_perfume_types_junction spt
    JOIN perfumes p ON spt.staging_id = p.staging_id
    JOIN perfume_types pt ON spt.type = pt.type;

ALTER TABLE
    perfumes DROP COLUMN staging_id;

DROP TABLE staging_perfume_types_junction;

DROP TABLE staging_perfumes;