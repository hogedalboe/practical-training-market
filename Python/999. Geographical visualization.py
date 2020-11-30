import visualization.geodata.geodata as gd
import config
import objects

db = objects.Database(config.server, config.database, config.user, config.password)

# Color scale for heat map.
# Color identifier names: https://matplotlib.org/3.1.0/gallery/color/named_colors.html
dict_colorScale = {10:'gainsboro', 15:'rosybrown', 20:'indianred', 25:'firebrick', 30:'darkred', 35:'black'}

# Get demographical data.
df_MunicipalityCommute = db.Read("SELECT municipalitycode, avgcommutekm FROM municipalitydemographics WHERE yearofmeasurement = 2018")

# Determine 'heat' of municipality.
dict_HeatMap = {}
for i, row in df_MunicipalityCommute.iterrows():
    for key, color in dict_colorScale.items():
        if row['avgcommutekm'] > key:
            dict_HeatMap['0'+str(int(row['municipalitycode']))] = color

gd.GeographicalVisualizer(dict_SubnationalColor=dict_HeatMap, path_Shapefile='KOMMUNE.shp', sf_SubnationalColumn="KOMKODE").plot_map('municipality_commute.png')

