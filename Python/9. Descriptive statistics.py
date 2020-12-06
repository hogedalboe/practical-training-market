import visualization.heatmap.heatmap as hm
import config
import objects

db = objects.Database(config.server, config.database, config.user, config.password)

################################################################################################################################ Determine ratio values between approvals and combined approvals

df_approvals = db.Read("SELECT * FROM approval")
df_combinedapprovals = db.Read("SELECT * FROM combinedapproval")

# Get the ratio between 
approvalRatio = df_approvals['approvalamount'].mean() / df_approvals['currentamount'].mean()
combinedapprovalRatio = df_combinedapprovals['approvalamount'].mean() / df_combinedapprovals['currentamount'].mean()

print(str(approvalRatio))
print(str(combinedapprovalRatio))

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
