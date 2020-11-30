SELECT * 
FROM postalarea
WHERE postalcode NOT IN(SELECT postalcode FROM distance)