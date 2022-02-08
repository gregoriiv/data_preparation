import json
import sys
sys.path.insert(0,"..")
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from config.config import Config

config_ways = Config("ways")
variable_container_ways = config_ways.preparation['variable_container']

network_islands = f'''

--Mark network islands in the network
--Update  "configuration" set tag_id = 701, tag_value = 'network_island' WHERE NOT EXISTS (Select tag_id, tag_value From "configuration" where tag_id = 701 and tag_value = 'network_island');
INSERT INTO "configuration" (tag_id, tag_value) VALUES (701, 'network_island');

DROP TABLE IF EXISTS network_islands; 
CREATE TABLE network_islands AS 
WITH RECURSIVE ways_no_islands AS (
	SELECT id,geom FROM 
	(SELECT id,geom
	FROM ways w
	WHERE w.tag_id NOT IN (SELECT UNNEST(ARRAY{variable_container_ways["excluded_class_id_walking"]}))
	AND w.tag_id NOT IN (SELECT UNNEST(ARRAY{variable_container_ways["excluded_class_id_cycling"]}))
	AND (
	(w.foot NOT IN (SELECT UNNEST(ARRAY{variable_container_ways["categories_no_foot"]})) OR foot IS NULL)
	OR
	(w.bicycle NOT IN (SELECT UNNEST(ARRAY{variable_container_ways["categories_no_bicycle"]})) OR bicycle IS NULL))
	LIMIT 1) x
	UNION 
	SELECT w.id,w.geom
	FROM ways w, ways_no_islands n
	WHERE ST_Intersects(n.geom,w.geom)
	AND w.tag_id NOT IN (SELECT UNNEST(ARRAY{variable_container_ways["excluded_class_id_walking"]}))
	AND w.tag_id NOT IN (SELECT UNNEST(ARRAY{variable_container_ways["excluded_class_id_cycling"]}))
	AND (w.foot NOT IN (SELECT UNNEST(ARRAY{variable_container_ways["categories_no_foot"]})) OR foot IS NULL)
) 
SELECT w.id  
FROM (
	SELECT w.id
	FROM ways w
	LEFT JOIN ways_no_islands n
	ON w.id = n.id
	WHERE n.id IS null
) x, ways w
WHERE w.id = x.id
AND w.tag_id NOT IN (SELECT UNNEST(ARRAY{variable_container_ways["excluded_class_id_walking"]}))
AND w.tag_id NOT IN (SELECT UNNEST(ARRAY{variable_container_ways["excluded_class_id_cycling"]}))
AND (w.foot NOT IN (SELECT UNNEST(ARRAY{variable_container_ways["categories_no_foot"]})) OR foot IS NULL); 

ALTER TABLE network_islands ADD PRIMARY KEY(id);
UPDATE ways w SET tag_id = 701
FROM network_islands n
WHERE w.id = n.id; 

'''