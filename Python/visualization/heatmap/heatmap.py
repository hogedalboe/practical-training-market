import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns
import os
import collections

cwd = os.path.dirname(__file__)

# https://download.kortforsyningen.dk/content/danmarks-administrative-geografiske-inddeling-110000
# https://towardsdatascience.com/mapping-geograph-data-in-python-610a963d2d7f
# https://matplotlib.org/3.1.0/gallery/color/named_colors.html

class GeographicalVisualizer:

    def __init__(self, dict_SubnationalColor, path_Shapefile, sf_SubnationalColumn, dict_ColorScale={}):
        """
        Example parameters:
            dict_SubnationalColor={'Thisted':'rosybrown', 'Lemvig':'darkred'},
            path_Shapefile='KOMMUNE.shp', 
            sf_SubnationalColumn="KOMNAVN"
        """

        self.dict_SubnationalColor = dict_SubnationalColor
        self.sf_SubnationalColumn = sf_SubnationalColumn
        self.dict_ColorScale = collections.OrderedDict(sorted(dict_ColorScale.items()))

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
    
    def plot_map(self, 
        output_filename, 
        boundaryColor='black', 
        title='', 
        figsize=(30,25), 
        gridColor='white', 
        showAxes=False, 
        scaleTextBefore='', 
        scaleTextAfter='',
        scaleTextAdjustLeft=25000,
        scaleValueTextSize=25,
         x_lim=None, y_lim=None):

        plt.clf()
        self.output_filename = output_filename

        plt.figure(figsize = figsize)
        fig, ax = plt.subplots(figsize = figsize)
        fig.suptitle(title, fontsize=48)

        # Color palette and scale values.
        xpos_rectangle = 865000
        ypos_rectangle = 6380000
        widthHeight = 35000
        for key, color in self.dict_ColorScale.items():

            # Scale value text.
            ax.text(xpos_rectangle-15000-scaleTextAdjustLeft, 
                ypos_rectangle+(widthHeight/2), 
                scaleTextBefore+str(key)+scaleTextAfter, 
                size=scaleValueTextSize, 
                color='black',
                fontfamily='Franklin Gothic Medium'
            )

            # Rectangle.
            rect = Rectangle((xpos_rectangle, ypos_rectangle), widthHeight, widthHeight, color=color)
            ax.add_patch(rect)
            ypos_rectangle -= widthHeight

        # Subnational boundaries.
        for shape in self.sf.shapeRecords():
            x = [i[0] for i in shape.shape.points[:]]
            y = [i[1] for i in shape.shape.points[:]]
            ax.plot(x, y, boundaryColor)
        
        # Subnational area.
        for subnational, color in self.dict_SubnationalColor.items():
            dfIndexes = list(self.df_Shapes[self.df_Shapes[self.sf_SubnationalColumn] == subnational].index)

            #indicateName = True

            for dfIndex in dfIndexes:
                shape_ex = self.sf.shape(dfIndex)
                x_lon = np.zeros((len(shape_ex.points),1))
                y_lat = np.zeros((len(shape_ex.points),1))

                for ip in range(len(shape_ex.points)):
                    x_lon[ip] = shape_ex.points[ip][0]
                    y_lat[ip] = shape_ex.points[ip][1]

                ax.fill(x_lon, y_lat, color)

                # Subnational name.
                #if indicateName == True:
                #    x0 = np.mean(x_lon)
                #    y0 = np.mean(y_lat)
                #    plt.text(x0, y0, 'test', fontsize=10, color='white')
                #    indicateName = False
        
        if (x_lim != None) & (y_lim != None):     
            plt.xlim(x_lim)
            plt.ylim(y_lim)
        
        plt.grid(color=gridColor)

        if not showAxes:
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
        
        # Save map.
        plt_path = os.path.join(cwd, 'output', self.output_filename)
        plt.savefig(plt_path, bbox_inches='tight', transparent='True', pad_inches=0)
