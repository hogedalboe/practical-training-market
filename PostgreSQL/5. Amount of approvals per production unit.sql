-- Getting the production units with the most approvals.
SELECT productionunit.*, COUNT(approval.*) AS number_of_approvals       
FROM productionunit
LEFT JOIN approval
	ON productionunit.pnum = approval.pnum
GROUP BY
    productionunit.pnum
ORDER BY number_of_approvals DESC;

-- Getting the average number of approvals per production unit.
SELECT AVG(number_of_approvals)
FROM (
	SELECT productionunit.*, COUNT(approval.*) AS number_of_approvals       
	FROM productionunit
	LEFT JOIN approval
		ON productionunit.pnum = approval.pnum
	GROUP BY
		productionunit.pnum
	ORDER BY number_of_approvals DESC
);
