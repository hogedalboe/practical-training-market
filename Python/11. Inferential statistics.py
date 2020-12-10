import config
import objects

db = objects.Database(config.server, config.database, config.user, config.password)

# Get all data of relevance for the descriptive statistical analysis.
df_Master = db.Read(
    """
    SELECT 
        combinedapproval.pnum,
        productionunit.cvrnum,
        combinedapproval.edunum,
        productionunit.postalcode,
        municipality.municipalitycode,
        region.regioncode,
        combinedapproval.approvalamount, 
        combinedapproval.currentamount, 
        combinedapproval.nearestfacilitykm,
        company.sectorcode,
        company.businesscode,
        company.employees,
        extract(year FROM company.established)::int as established,
        education.committeecode,
        municipalitydemographics.yearofmeasurement,
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
            LEFT JOIN region on region.regioncode = municipality.regioncode
            LEFT JOIN municipalitydemographics on municipalitydemographics.municipalitycode = municipality.municipalitycode
                AND municipalitydemographics.yearofmeasurement = 2018

    WHERE approvalamount <> 0   
    """
)

################################################################################################################################ 






################################################################################################################################ Test: Multiple linear regression

# https://datatofish.com/statsmodels-linear-regression/

import statsmodels.api as sm

# Does geographical variables influence the current amount of employed students?
df_Geography = df_Master[['currentamount', 'nearestfacilitykm', 'avgcommutekm']].dropna()

X = df_Geography[['nearestfacilitykm', 'avgcommutekm']]
Y = df_Geography['currentamount']
X = sm.add_constant(X)

model = sm.OLS(Y, X).fit()
print_model = model.summary()
print(print_model)