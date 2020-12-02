/*
Limitation codes causing exclusion:
1141 2 pr. år
1152 Overlap max. 12 mdr.
1158 Overlap max. 18 mdr.
1159 Overlap max 24 mdr.
1161 Min. 1 år imellem
1162 Min. 1,5 år imellem
1164 Ny efter 1/2 læretid
1204 Max 3 mdr. dette sted
1206 Max 6 mdr. dette sted
1209 Max 9 mdr. dette sted
1212 Max 12 mdr. dette sted
1225 Max 24 mdr. dette sted
1230 Max 1/2 læretid her
1096 Kun til FGU
1097 Kun til VFU (virksomhedsforlagt undervisning, SKP)
1100 Gælder et specifikt uddannelsesforhold
*/

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