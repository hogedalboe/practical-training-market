-- Count the companies.
SELECT COUNT(*)
FROM company c
    LEFT JOIN productionunit p ON c.cvrnum = p.cvrnum
WHERE p.cvrnum IS NULL;

-- Delete the companies.
DELETE FROM company c1
WHERE c1.cvrnum IN (
	SELECT c2.cvrnum
	FROM company c2
		LEFT JOIN productionunit p ON c2.cvrnum = p.cvrnum
	WHERE p.cvrnum IS NULL
);