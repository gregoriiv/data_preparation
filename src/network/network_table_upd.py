network_table_upd = '''
DROP TABLE IF EXISTS ways_temp;
DROP TABLE IF EXISTS ways_vertices_pgr_temp;
CREATE TABLE ways_temp AS TABLE ways;
CREATE TABLE ways_vertices_pgr_temp AS TABLE ways_vertices_pgr;
DROP TABLE IF EXISTS ways;
DROP TABLE IF EXISTS ways_vertices_pgr;
ALTER TABLE ways_temp RENAME TO ways;
ALTER TABLE ways_vertices_pgr_temp RENAME TO ways_vertices_pgr;

ALTER TABLE ways
DROP COLUMN RULE,DROP COLUMN x1,DROP COLUMN x2,DROP COLUMN y1,DROP COLUMN y2, DROP COLUMN priority,
DROP COLUMN length,DROP COLUMN cost,DROP COLUMN reverse_cost, DROP COLUMN cost_s, DROP COLUMN reverse_cost_s, 
DROP COLUMN source_osm, DROP COLUMN target_osm;

ALTER TABLE ways_vertices_pgr DROP COLUMN chk, DROP COLUMN ein, DROP COLUMN eout, DROP COLUMN lon, DROP COLUMN lat;

ALTER TABLE ways rename column gid to id;
ALTER TABLE ways rename column the_geom to geom;
ALTER TABLE ways_vertices_pgr rename column the_geom to geom;
ALTER TABLE ways alter column target type int4;
ALTER TABLE ways alter column source type int4;

ALTER TABLE ways ADD PRIMARY KEY (id);
ALTER TABLE ways_vertices_pgr ADD PRIMARY KEY (id);

CREATE INDEX ON ways USING GIST(geom);
CREATE INDEX ON ways_vertices_pgr USING GIST(geom)

ALTER TABLE ways 
ADD COLUMN bicycle text, ADD COLUMN foot TEXT, ADD COLUMN length_3857 float, ADD COLUMN coordinates_3857 json; /*, ADD COLUMN oneway TEXT;*/ 
'''