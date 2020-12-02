import visualization.heatmap.heatmap as hm
import config
import objects

db = objects.Database(config.server, config.database, config.user, config.password)

# Color scale for heat map.
dict_ColorScales = {
    # Color references: https://matplotlib.org/3.1.0/gallery/color/named_colors.html / https://towardsdatascience.com/mapping-geograph-data-in-python-610a963d2d7f
    'blue':{10:'aqua', 15:'deepskyblue', 20:'mediumslateblue', 25:'mediumblue', 30:'midnightblue', 35:'black'},
    'red':{10:'gainsboro', 15:'rosybrown', 20:'indianred', 25:'firebrick', 30:'darkred', 35:'black'},
    'gray':{10:'snow', 15:'darkgray', 20:'slategray', 25:'dimgray', 30:'darkslategray', 35:'black'},
    'sunset':{10:'lightyellow', 15:'khaki', 20:'gold', 25:'goldenrod', 30:'orangered', 35:'darkred'},
    'purple':{10:'#dadaebFF', 15:'#bcbddcF0', 20:'#9e9ac8F0', 25:'#807dbaF0', 30:'#6a51a3F0', 35:'#54278fF0'},
    'YlGnBu':{10:'#c7e9b4', 15:'#7fcdbb', 20:'#41b6c4', 25:'#1d91c0', 30:'#225ea8', 35:'#253494'},
}

################################################################################################################################ Test

# Get demographical data.
df_MunicipalityCommute = db.Read("SELECT municipalitycode, avgcommutekm FROM municipalitydemographics WHERE yearofmeasurement = 2018")

# Determine 'heat' of municipality.
dict_HeatMap = {}
for i, row in df_MunicipalityCommute.iterrows():
    for key, color in dict_ColorScales['blue'].items():
        if row['avgcommutekm'] > key:
            dict_HeatMap['0'+str(int(row['municipalitycode']))] = color

hm.GeographicalVisualizer(dict_SubnationalColor=dict_HeatMap, 
    path_Shapefile='KOMMUNE.shp', 
    sf_SubnationalColumn="KOMKODE", 
    dict_ColorScale=dict_ColorScales['blue']
).plot_map('test.png', 
    scaleTextBefore='> ', 
    scaleTextAfter=' km', 
    scaleTextAdjustLeft=25000
)

################################################################################################################################ ...