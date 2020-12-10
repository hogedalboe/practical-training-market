SELECT 
	combinedapproval.pnum,
	productionunit.cvrnum,
	combinedapproval.edunum,
	productionunit.postalcode,
	municipality.municipalitycode,
	region.regioncode,
	regiondemographics.yearofmeasurement as regionyearofmeasurement,
	regiondemographics.population as regionpopulation,
	combinedapproval.approvalamount, 
	combinedapproval.currentamount, 
	combinedapproval.nearestfacilitykm,
	company.sectorcode,
	company.businesscode,
	company.employees,
	extract(year FROM company.established)::int as established,
	education.committeecode,
	municipalitydemographics.yearofmeasurement as municipalityyearofmeasurement,
	municipalitydemographics.population as municipalitypopulation,
	municipalitydemographics.avgcommutekm,
	municipalitydemographics.employmentrate,
	municipalitydemographics.employmentavailabilityrate,
	municipalitydemographics.yearlydisposableincome,
	financial.pubyear,
	financial.liquidityratio,
	financial.roi,
	financial.solvencyratio,
	financial.netturnover,
	financial.grossprofit,
	financial.equity,
	financial.netresult,
	financial.balance,
	financial.currency
	
	FROM combinedapproval
	
		LEFT JOIN productionunit on productionunit.pnum = combinedapproval.pnum
		LEFT JOIN company on company.cvrnum = productionunit.cvrnum
		LEFT JOIN education on education.edunum = combinedapproval.edunum
		LEFT JOIN financial on financial.cvrnum = company.cvrnum 
			AND financial.pubyear > 2017
			AND financial.currency = 'DKK'
			AND financial.pubyear = (SELECT MAX(pubyear) FROM financial WHERE financial.cvrnum = company.cvrnum)
		LEFT JOIN postalarea on postalarea.postalcode = productionunit.postalcode
		LEFT JOIN municipality on municipality.municipalitycode = postalarea.municipalitycode
		LEFT JOIN municipalitydemographics on municipalitydemographics.municipalitycode = municipality.municipalitycode
			AND municipalitydemographics.yearofmeasurement = 2018
		LEFT JOIN region on region.regioncode = municipality.regioncode
		LEFT JOIN regiondemographics on regiondemographics.regioncode = region.regioncode
			AND municipalitydemographics.yearofmeasurement = 2018

WHERE approvalamount <> 0   