import visualization.heatmap.heatmap as hm
import config
import objects

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np 
import scipy.stats

db = objects.Database(config.server, config.database, config.user, config.password)

# Get query for obtaining master data.
masterQuery = ""
with open(r'C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\PostgreSQL\10. Master data query.sql', 'r') as f:
    masterQuery = f.read()

# Get all data of relevance for the descriptive statistical analysis.
df_Master = db.Read(masterQuery)

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

################################################################################################################################ Univariate shapes of approval/employment/propensity data

df_Key = df_Master[['currentamount', 'approvalamount', 'propensity']].dropna()

def univariate(column, x_name, countValue, continuous=True, color='blue', kde_bandwidth=1, plot_note_fontsize=8, plot_title_fontsize=12):
    print("-------------------------------------------------------")

    print("Univariate measures for variable '{0}'".format(x_name))

    # Univariate data.
    x = df_Key[column].rename(x_name)

    # Number of combined approvals with an x value of 'countValue'.
    num_countValue = len(df_Key.loc[df_Key[column] == 0.0].index)
    print("\tNumber of combined approvals with an x value of '{0}': {1}.".format(str(countValue), str(num_countValue)))

    # Sample size.
    print("\tSample size: {0}.".format(str(len(df_Key.index))))

    # Mean.

    # Median.


    print("-------------------------------------------------------")

    # If the variable is continuous (ie. quantitative), visualize it with a histogram.
    if continuous:
        # Histogram (https://seaborn.pydata.org/generated/seaborn.histplot.html).
        sns.histplot(x, color=color)
        plt.title("Plot A", loc='left', fontsize=plot_title_fontsize)
        plt.xlabel("{0} (X)".format(x_name))
        plt.show()

        # Kernel density estimate (KDE) method of selecting optimal bandwidth via 'mean integrated square error risk function'.
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gaussian_kde.html
        # Scott, D. W. 2014. Multivariate density estimation: theory, practice, and visualization. Second edition., Hoboken, New Jersey: Wiley.
        
        # Kernel density estimate (KDE) distribution (https://seaborn.pydata.org/generated/seaborn.kdeplot.html).
        sns.kdeplot(x, shade=True, bw_method='scott', color=color)
        plt.title("Plot B", loc='left', fontsize=plot_title_fontsize)
        plt.xlabel("Kernel density estimate (KDE) distribution of X")
        plt.title("KDE bandwidth = {0}".format(str(kde_bandwidth)), loc='right', fontsize=plot_note_fontsize)
        plt.show()

        # Box-Cox transformation of skewed/non-Gaussian variables (https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.boxcox.html).
        df_xt = df_Key.loc[df_Key[column] > 0.0] # Values must be >0.
        xt = df_xt[column].rename("Box-Cox transformation of '{0}'".format(x_name))
        xt, xt_lambda = scipy.stats.boxcox(xt)
        sns.histplot(xt, color=color)
        plt.title("Plot C", loc='left', fontsize=plot_title_fontsize)
        plt.xlabel("Frequency distribution of X following Box-Cox transformation")
        plt.title("Power parameter (λ) = {0}".format(str(round(xt_lambda,2))), loc='right', fontsize=plot_note_fontsize)
        plt.show()

        # Kernel density estimate (KDE) distribution of the Box-Cox-transformed data.
        sns.kdeplot(xt, shade=True, bw=kde_bandwidth, color=color)
        plt.title("Plot D", loc='left', fontsize=plot_title_fontsize)
        plt.xlabel("Kernel density estimate (KDE) distribution of the Box-Cox-transformed data")
        plt.title("KDE bandwidth = {0}".format(str(kde_bandwidth)), loc='right', fontsize=plot_note_fontsize)
        plt.title("Power parameter (λ) = {0}".format(str(round(xt_lambda,2))), loc='center', fontsize=plot_note_fontsize)
        plt.show()

    # If the variable is discrete (ie. categorical), visualize it with a bar chart.
    else:
        # Bar chart (https://seaborn.pydata.org/generated/seaborn.countplot.html).
        sns.countplot(x=x, color=color)
        plt.show()

univariate('approvalamount', 'Number of vocational students a production unit is approved for', 0.0)
univariate('currentamount', 'Current number of employed vocational students', 0.0)
univariate('propensity', 'Propensity to employ vocational students', 0.0)

input("Stop")


















import statsmodels.formula.api as smf
import statsmodels.stats.multicomp as multi
import scipy
from scipy.stats import pearsonr
import pandas as pd
from seaborn import regplot
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.lmplot(x="internetuserate", y="breastcancerper100th", data=df2, fit_reg=False)
plt.title("Internet Use Rate and Breast Cancer Per 100k")
plt.show()












# Use Shapiro-Wilk test to determine whether the approval/employment/propensity data have a Gaussian distribution.
from scipy.stats import shapiro

####################################
import matplotlib.pyplot as plt
data = list(df_Key.loc[df_Key['currentamount'] != 0.0]['currentamount'])
plt.hist(data)
plt.show()
####################################

input("stop")

stat, p = shapiro(list(df_Key['currentamount']))
print('stat=%.3f, p=%.3f' % (stat, p))
if p > 0.05:
	print('Probably Gaussian')
else:
	print('Probably not Gaussian')









input("stop")

################################################################################################################################ Test: Heat map

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