SELECT * 
FROM productionunit
WHERE postalcode NOT IN(SELECT postalcode FROM distance)