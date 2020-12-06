import visualization.heatmap.heatmap as hm
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

print(df_Master.head(5))
input("stop")

################################################################################################################################ Determine ratio values between approvals and combined approvals

def approvalRatios():
    df_approvals = db.Read("SELECT * FROM approval")
    df_combinedapprovals = db.Read("SELECT * FROM combinedapproval")

    # Get the ratio between 
    approvalRatio = df_approvals['approvalamount'].mean() / df_approvals['currentamount'].mean()
    combinedapprovalRatio = df_combinedapprovals['approvalamount'].mean() / df_combinedapprovals['currentamount'].mean()

    print(str(approvalRatio))
    print(str(combinedapprovalRatio))

#approvalRatios()

################################################################################################################################ ...

















################################################################################################################################ Test

# Get demographical data.
df_MunicipalityCommute = db.Read("SELECT municipalitycode, avgcommutekm FROM municipalitydemographics WHERE yearofmeasurement = 2018")

# Determine 'heat' of municipality.
dict_HeatMap = {}
for i, row in df_MunicipalityCommute.iterrows():
    for key, color in hm.dict_ColorScales['blue'].items():
        if row['avgcommutekm'] > key:
            dict_HeatMap['0'+str(int(row['municipalitycode']))] = color

hm.GeographicalVisualizer(dict_SubnationalColor=dict_HeatMap, 
    path_Shapefile='KOMMUNE.shp', 
    sf_SubnationalColumn='KOMKODE', 
    dict_ColorScale=hm.dict_ColorScales['blue']).plot_map('test.png', 
        scaleTextBefore='> ', 
        scaleTextAfter=' km', 
        scaleTextAdjustLeft=25000
    )










################################################################################################################################ Disconnect database

db.Disconnect()