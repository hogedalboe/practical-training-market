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

class GeographicalVisualizer:

    def __init__(self, dict_SubnationalColor, path_Shapefile, sf_SubnationalColumn):
        """
        Example parameters:
            dict_SubnationalColor={'Thisted':'rosybrown', 'Lemvig':'darkred'},
            path_Shapefile='KOMMUNE.shp', 
            sf_SubnationalColumn="KOMNAVN"
        """

        self.dict_SubnationalColor = dict_SubnationalColor
        self.sf_SubnationalColumn = sf_SubnationalColumn

        # Initializing vizualization set.
        sns.set(style="whitegrid", palette="pastel", color_codes=True)
        sns.mpl.rc("figure", figsize=(10,6))

        # Opening vector map.
        shp_path = os.path.join(cwd, "ADM", path_Shapefile)
        self.sf = shp.Reader(shp_path, encoding="ISO-8859-1")

        # Get dataframe for shapes.
        self.df_Shapes = self.sf_to_df(self.sf)

        print("\nColumns in shape data: \n" + str(self.df_Shapes.columns.values.tolist()))
        print("\nShape dataframe: \n" + str(self.df_Shapes[['REGIONKODE', 'REGIONNAVN', 'KOMKODE', 'KOMNAVN', 'coords']].head(99)))
    
    def sf_to_df(self, sf):
        fields = [x[0] for x in sf.fields][1:]
        records = sf.records()
        shps = [s.points for s in sf.shapes()]
        df = pd.DataFrame(columns=fields, data=records)
        df = df.assign(coords=shps)
        return df
    
    def plot_map(self, output_filename, boundaryColor='black', title='', figsize=(30,25), gridColor='white', showAxes=False, x_lim=None, y_lim=None):
        plt.clf()
        self.output_filename = output_filename

        plt.figure(figsize = figsize)
        fig, ax = plt.subplots(figsize = figsize)
        fig.suptitle(title, fontsize=48)

        # Subnational boundaries.
        for shape in self.sf.shapeRecords():
            x = [i[0] for i in shape.shape.points[:]]
            y = [i[1] for i in shape.shape.points[:]]
            ax.plot(x, y, boundaryColor)
        
        # Subnational area.
        for subnational, color in self.dict_SubnationalColor.items():
            dfIndexes = list(self.df_Shapes[self.df_Shapes[self.sf_SubnationalColumn] == subnational].index)

            for dfIndex in dfIndexes:
                shape_ex = self.sf.shape(dfIndex)
                x_lon = np.zeros((len(shape_ex.points),1))
                y_lat = np.zeros((len(shape_ex.points),1))

                for ip in range(len(shape_ex.points)):
                    x_lon[ip] = shape_ex.points[ip][0]
                    y_lat[ip] = shape_ex.points[ip][1]

                ax.fill(x_lon,y_lat, color)
        
        if (x_lim != None) & (y_lim != None):     
            plt.xlim(x_lim)
            plt.ylim(y_lim)
        
        plt.grid(color=gridColor)

        if not showAxes:
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
        
        # Save map.
        plt_path = os.path.join(cwd, "output", self.output_filename)
        plt.savefig(plt_path)