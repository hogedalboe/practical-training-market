SELECT 
	combinedapproval.pnum,
	productionunit.cvrnum,
	combinedapproval.edunum,
	education.name as eduname,
	committee.committeecode,
	committee.name as committeename,
	productionunit.postalcode,
	municipality.municipalitycode,
	municipality.name as municipalityname,
	region.regioncode,
	region.name as regionname,
	regiondemographics.yearofmeasurement as regionyearofmeasurement,
	regiondemographics.population as regionpopulation,
	combinedapproval.approvalamount as approvalnumber, 
	combinedapproval.currentamount as currentnumber, 
	combinedapproval.currentamount / combinedapproval.approvalamount as propensity,
	combinedapproval.nearestfacilitykm,
	company.sectorcode,
	sector.sectorname,
	company.businesscode,
	business.name as businesstype,
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
			AND financial.pubyear = (
				SELECT MAX(pubyear) FROM financial WHERE financial.cvrnum = company.cvrnum
			)
		LEFT JOIN postalarea on postalarea.postalcode = productionunit.postalcode
		LEFT JOIN municipality on municipality.municipalitycode = postalarea.municipalitycode
		LEFT JOIN municipalitydemographics on municipalitydemographics.municipalitycode = municipality.municipalitycode
			AND municipalitydemographics.yearofmeasurement = 2018
		LEFT JOIN region on region.regioncode = municipality.regioncode
		LEFT JOIN regiondemographics on regiondemographics.regioncode = region.regioncode
			AND regiondemographics.yearofmeasurement = 2019
		LEFT JOIN committee on committee.committeecode = education.committeecode
		LEFT JOIN sector on sector.sectorcode = company.sectorcode
		LEFT JOIN business on business.businesscode = company.businesscode

WHERE combinedapproval.approvalamount <> 0   