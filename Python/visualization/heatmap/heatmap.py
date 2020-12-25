import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns
import os
import collections

cwd = os.path.dirname(__file__)

# Shape files (ArcGIS) from: https://download.kortforsyningen.dk/content/danmarks-administrative-geografiske-inddeling-110000
# Heat map functionality inspired by: https://towardsdatascience.com/mapping-geograph-data-in-python-610a963d2d7f

# Color scale for heat map.
dict_ColorScales = {

    # Color scale resources: 
    #       https://matplotlib.org/3.1.0/gallery/color/named_colors.html
    #       https://towardsdatascience.com/mapping-geograph-data-in-python-610a963d2d7f
    #       https://betterfigures.org/2015/06/23/picking-a-colour-scale-for-scientific-graphics/
    #       https://colorbrewer2.org/#type=sequential&scheme=YlGnBu&n=6

    # Test:
    'blue':{10:'aqua', 15:'deepskyblue', 20:'mediumslateblue', 25:'mediumblue', 30:'midnightblue', 35:'black'},
    'red':{10:'gainsboro', 15:'rosybrown', 20:'indianred', 25:'firebrick', 30:'darkred', 35:'black'},
    'gray':{10:'snow', 15:'darkgray', 20:'slategray', 25:'dimgray', 30:'darkslategray', 35:'black'},
    'sunset':{10:'lightyellow', 15:'khaki', 20:'gold', 25:'goldenrod', 30:'orangered', 35:'darkred'},
    'purple':{10:'#dadaebFF', 15:'#bcbddcF0', 20:'#9e9ac8F0', 25:'#807dbaF0', 30:'#6a51a3F0', 35:'#54278fF0'},
    'YlGnBu':{10:'#c7e9b4', 15:'#7fcdbb', 20:'#41b6c4', 25:'#1d91c0', 30:'#225ea8', 35:'#253494'},

    # Custom:
    'currentnumber':{0: '#5F021F', 1:'#ffffcc', 10: '#c7e9b4', 20: '#7fcdbb', 30: '#41b6c4', 40: '#2c7fb8', 50: '#253494'},
    'propensity':{0.0:'#5F021F', 0.1: '#d0d1e6', 0.2: '#a6bddb', 0.3: '#67a9cf', 0.4: '#1c9099', 0.5: '#016c59'},
    'currentnumberUnadjusted':{0:'#ffffcc', 100: '#c7e9b4', 200: '#7fcdbb', 300: '#41b6c4', 400: '#2c7fb8', 500: '#253494'},
    'commuting':{10:'#f7f7f7', 15: '#d9d9d9', 20: '#bdbdbd', 25: '#969696', 30: '#636363', 35: '#252525'},

    
    # Yellow/green/blue:
    #'colorbrewer_YlGnBu':{1:'#ffffcc', 2: '#c7e9b4', 3: '#7fcdbb', 4: '#41b6c4', 5: '#2c7fb8', 6: '#253494'},
    'colorbrewer_GnBu':{1:'#f0f9e8', 2: '#ccebc5', 3: '#a8ddb5', 4: '#7bccc4', 5: '#43a2ca', 6: '#0868ac'},
    #'colorbrewer_PuBuGn':{1:'#f6eff7', 2: '#d0d1e6', 3: '#a6bddb', 4: '#67a9cf', 5: '#1c9099', 6: '#016c59'},

    # Yellow/orange/brown/red:
    'colorbrewer_YlOrBr':{1:'#ffffd4', 2: '#fee391', 3: '#fec44f', 4: '#fe9929', 5: '#d95f0e', 6: '#993404'},
    'colorbrewer_YlOrRd':{1:'#ffffb2', 2: '#fed976', 3: '#feb24c', 4: '#fd8d3c', 5: '#f03b20', 6: '#bd0026'},
    'colorbrewer_Oranges':{1:'#feedde', 2: '#fdd0a2', 3: '#fdae6b', 4: '#fd8d3c', 5: '#e6550d', 6: '#a63603'},

    # Red/purple:
    'colorbrewer_PuRd':{1:'#f1eef6', 2: '#d4b9da', 3: '#c994c7', 4: '#df65b0', 5: '#dd1c77', 6: '#980043'},
    'colorbrewer_RdPu':{1:'#feebe2', 2: '#fcc5c0', 3: '#fa9fb5', 4: '#f768a1', 5: '#c51b8a', 6: '#7a0177'},
    'colorbrewer_Purples':{1:'#f2f0f7', 2: '#dadaeb', 3: '#bcbddc', 4: '#9e9ac8', 5: '#756bb1', 6: '#54278f'},


    # Reds
    'colorbrewer_Reds':{1:'#fee5d9', 2: '#fcbba1', 3: '#fc9272', 4: '#fb6a4a', 5: '#de2d26', 6: '#a50f15'},

    # Greys
    #'colorbrewer_Greys':{1:'#f7f7f7', 2: '#d9d9d9', 3: '#bdbdbd', 4: '#969696', 5: '#636363', 6: '#252525'}
}



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
        print("\nShape dataframe: \n" + str(self.df_Shapes[['REGIONKODE', 'REGIONNAVN', 'KOMKODE', 'KOMNAVN', 'coords']].head(3)))
    
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
        scaleValueTextSize=30,
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
