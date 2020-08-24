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

SELECT COUNT(*) FROM limits
WHERE limitationcode IN (SELECT limitationcode FROM limits_to_delete);