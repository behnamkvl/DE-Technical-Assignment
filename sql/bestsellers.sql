CREATE SCHEMA IF NOT EXISTS bestsellers;
SET search_path TO bestsellers;

create external schema spectrum
from data catalog
database 'spectrumdb'
iam_role 'arn:aws:iam::857369967123:role/MyRedshiftSpectrumRole'
create external database if not exists;


--------------Review [spectrum]------------------------------------------
create external table spectrum.reviews(
reviewerid varchar,
asin varchar,
reviewername varchar,
reviewtext varchar(max),
overall double precision,
summary varchar,
unixreviewtime integer,
reviewtime varchar
)
PARTITIONED BY (downloaded_at integer)
ROW FORMAT SERDE 
  'org.openx.data.jsonserde.JsonSerDe' 
  WITH SERDEPROPERTIES ( 
  'ignore.malformed.json' = 'true',
  'paths'='asin,helpful,overall,reviewText,reviewTime,reviewerID,reviewerName,summary,unixReviewTime') 
LOCATION 's3://behnam-test-bestsellers/review/';


--------------Review [redshift]------------------------------------------
create table if not exists bestsellers.reviews(
reviewerid varchar,
asin varchar,
reviewername varchar,
reviewtext varchar(max),
overall double precision,
summary varchar,
unixreviewtime integer,
reviewtime varchar
)

--------------Metadata [spectrum]-----------------------------------------
create external table spectrum.metadata(
asin varchar,
price double precision
)
PARTITIONED BY (downloaded_at integer)
ROW FORMAT SERDE 
  'org.openx.data.jsonserde.JsonSerDe' 
  WITH SERDEPROPERTIES ( 
  'ignore.malformed.json' = 'true',
  'paths'='asin,price') 
LOCATION 's3://behnam-test-bestsellers/metadata/';


--------------Metadata [redshift]-----------------------------------------
create table bestsellers.metadata(
asin varchar,
price double precision
)


------------MATERIALIZED VIEW [redshift]--------------------------------------------
CREATE MATERIALIZED VIEW bestsellers.review_joined_price
AS
SELECT 
r.reviewerid, r.asin, r.reviewername, r.reviewtext, r.overall, r.summary, r.unixreviewtime, r.reviewtime
, m.price
FROM bestsellers.reviews r
LEFT JOIN bestsellers.metadata m using(asin)
