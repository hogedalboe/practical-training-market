SELECT COUNT(*)
	FROM (
		SELECT DISTINCT ON (cvrnum) cvrnum
		FROM public.financial
		WHERE pubyear > 2017
	) AS temp;