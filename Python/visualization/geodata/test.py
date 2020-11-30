import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib.pyplot as plt
import seaborn as sns
import os

cwd = os.path.dirname(__file__)

# https://download.kortforsyningen.dk/content/danmarks-administrative-geografiske-inddeling-110000
# https://towardsdatascience.com/mapping-geograph-data-in-python-610a963d2d7f
# https://matplotlib.org/3.1.0/gallery/color/named_colors.html

# Initializing vizualization set.
sns.set(style="whitegrid", palette="pastel", color_codes=True)
sns.mpl.rc("figure", figsize=(10,6))

# Opening vector map.
shp_path = os.path.join(cwd, "ADM", "KOMMUNE.shp")
sf = shp.Reader(shp_path, encoding="ISO-8859-1")

# Inspecting shapefile record.
# print(str(sf.records()[0]))

def sf_to_df(sf):
    """
    Read a shapefile into a Pandas dataframe with a 'coords' column holding the geometry information. This uses the pyshp package.
    """
    fields = [x[0] for x in sf.fields][1:]
    records = sf.records()
    shps = [s.points for s in sf.shapes()]
    df = pd.DataFrame(columns=fields, data=records)
    df = df.assign(coords=shps)
    return df

# Get dataframe for shapes.
df_Shapes = sf_to_df(sf)

# Inspecting shape dataframe.
#print(df_Shapes.head())
#print(df_Shapes.columns.values.tolist())

def plot_map_fill_multiples_subnationals(subnationals, sf, x_lim=None, y_lim=None, figsize=(30,25), boundaryColor='k', fillColor='r', title=""):

    plt.figure(figsize = figsize)
    fig, ax = plt.subplots(figsize = figsize)
    fig.suptitle(title, fontsize=48)

    # Subnational boundaries.
    for shape in sf.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        ax.plot(x, y, boundaryColor)

    # Subnational area.        
    for subnational in subnationals:
        shape_ex = sf.shape(subnational)
        x_lon = np.zeros((len(shape_ex.points),1))
        y_lat = np.zeros((len(shape_ex.points),1))

        for ip in range(len(shape_ex.points)):
            x_lon[ip] = shape_ex.points[ip][0]
            y_lat[ip] = shape_ex.points[ip][1]

        ax.fill(x_lon,y_lat, fillColor)
    
    if (x_lim != None) & (y_lim != None):     
        plt.xlim(x_lim)
        plt.ylim(y_lim)

ids = list(df_Shapes[df_Shapes['KOMNAVN'] == 'Lemvig'].index)
plot_map_fill_multiples_subnationals("Multiple Shapes", ids, sf)
plt_path = os.path.join(cwd, "output", "output.png")
plt.savefig(plt_path)