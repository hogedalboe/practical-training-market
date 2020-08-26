-- Count the production units.
SELECT COUNT(*)
FROM productionunit p
    LEFT JOIN approval a ON p.pnum = a.pnum
WHERE a.pnum IS NULL;

-- Delete the production units.
DELETE FROM productionunit p1
WHERE p1.pnum IN (
	SELECT p2.pnum
	FROM productionunit p2
		LEFT JOIN approval a ON p2.pnum = a.pnum
	WHERE a.pnum IS NULL
);