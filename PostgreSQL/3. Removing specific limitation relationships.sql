-- Storing the limitation codes to remove.
DROP TABLE IF EXISTS limits_to_delete;
CREATE TEMP TABLE limits_to_delete (limitationcode INT);
INSERT INTO limits_to_delete VALUES (1141);
INSERT INTO limits_to_delete VALUES (1152);
INSERT INTO limits_to_delete VALUES (1158);
INSERT INTO limits_to_delete VALUES (1159);
INSERT INTO limits_to_delete VALUES (1161);
INSERT INTO limits_to_delete VALUES (1162);
INSERT INTO limits_to_delete VALUES (1164);
INSERT INTO limits_to_delete VALUES (1204);
INSERT INTO limits_to_delete VALUES (1206);
INSERT INTO limits_to_delete VALUES (1209);
INSERT INTO limits_to_delete VALUES (1212);
INSERT INTO limits_to_delete VALUES (1225);
INSERT INTO limits_to_delete VALUES (1230);
INSERT INTO limits_to_delete VALUES (1096);
INSERT INTO limits_to_delete VALUES (1097);
INSERT INTO limits_to_delete VALUES (1100);

-- Storing the limitation relationships (limitation key relationships must be removed before approvals due to foreign key constraints).
DROP TABLE IF EXISTS temp_limits;
CREATE TEMP TABLE temp_limits AS
SELECT specnum, edunum, pnum FROM limits
WHERE limitationcode IN (SELECT limitationcode FROM limits_to_delete);

-- Removing limitation relationships.
DELETE FROM limits l
USING temp_limits tl
WHERE l.specnum = tl.specnum
	AND l.edunum = tl.edunum
	AND l.pnum = tl.pnum;

-- Removing approvals.
DELETE FROM approval a
USING temp_limits tl
WHERE a.specnum = tl.specnum
	AND a.edunum = tl.edunum
	AND a.pnum = tl.pnum;