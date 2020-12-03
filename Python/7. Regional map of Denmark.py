import visualization.heatmap.heatmap as hm
import config
import objects

db = objects.Database(config.server, config.database, config.user, config.password)

# Get regions and municipalities.
df_Regions = db.Read("SELECT regioncode, name FROM region")
df_Municipalities = db.Read("SELECT municipalitycode, regioncode FROM municipality")

# Assign distinct colors to each region (5).
regionColors = ['khaki', 'darkseagreen', 'tomato', 'teal', 'cornflowerblue']
dict_ColorScale = {}

# Set colors of each region.
dict_HeatMap = {}
for i, rowReg in df_Regions.iterrows():

    # Determine region color.
    dict_ColorScale[rowReg['name']] = regionColors[i]

    # Color each municipality according to region.
    for j, rowMun in df_Municipalities.iterrows():
        if rowReg['regioncode'] == rowMun['regioncode']:
            dict_HeatMap['0'+str(int(rowMun['municipalitycode']))] = regionColors[i]

hm.GeographicalVisualizer(dict_SubnationalColor=dict_HeatMap, 
    path_Shapefile='KOMMUNE.shp', 
    sf_SubnationalColumn='KOMKODE', 
    dict_ColorScale=dict_ColorScale).plot_map('Regional map of Denmark.png', 
        boundaryColor='lightgray', 
        scaleTextAdjustLeft=75000,
        scaleValueTextSize=30
    )