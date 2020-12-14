import visualization.heatmap.heatmap as hm
import config
import objects

import matplotlib.pyplot as plt
import seaborn as sns
import pandas
import numpy as np 
import scipy.stats
from scipy.stats import shapiro

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

def univariate(column, x_name, countValue, continuous=True, color='blue', plot_note_fontsize=8, plot_title_fontsize=12):
    print("-------------------------------------------------------")

    print("Univariate measures for variable '{0}'".format(x_name))

    # Univariate data.
    x = df_Key[column].rename(x_name)

    # Number of combined approvals with an x value of 'countValue'.
    num_countValue = len(df_Key.loc[df_Key[column] == 0.0].index)
    print("\tNumber of combined approvals with an x value of '{0}': {1}.".format(str(countValue), str(num_countValue)))

    # If the variable is continuous (ie. quantitative), visualize it with a histogram.
    if continuous:
        # Create four quadrants (using axis as table) for structuring the plots.
        fig, axs = plt.subplots(4, 1)

        # Histogram (https://seaborn.pydata.org/generated/seaborn.histplot.html).
        #plt.figure(1)
        plt.sca(axs[0]) # If several columns, use 'axs[0,0]
        sns.histplot(x, color=color)
        plt.title("A", loc='left', fontsize=plot_title_fontsize, fontweight='bold')
        x_n = len(x.index)
        plt.title("n = {}".format(str(x_n)), loc='right', fontsize=plot_note_fontsize)
        plt.xlabel("{0} (X)".format(x_name))
        plt.tight_layout()

        # Kernel density estimate (KDE) method of selecting optimal bandwidth via 'mean integrated square error risk function'.
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gaussian_kde.html
        # Theoretical source: Scott, D. W. 2014. Multivariate density estimation: theory, practice, and visualization. Second edition., Hoboken, New Jersey: Wiley.
        
        # Kernel smoothing bandwidth: Get kernel density estimate (KDE) bandwidth.
        x_kde = scipy.stats.gaussian_kde(x, 'scott')
        x_f = x_kde.covariance_factor()
        x_kde_bandwidth = x_f * x.std()

        # Kernel density estimate (KDE) distribution (https://seaborn.pydata.org/generated/seaborn.kdeplot.html).
        #plt.figure(2)
        plt.sca(axs[1])
        sns.kdeplot(x, shade=True, bw_method='scott', color=color)
        plt.title("B", loc='left', fontsize=plot_title_fontsize, fontweight='bold')
        x_n = len(x.index)
        plt.xlabel("Kernel density estimate (KDE) distribution of X")
        plt.title("n = {0}".format(str(x_n)), loc='right', fontsize=plot_note_fontsize)
        plt.title("KDE bandwidth = {0}".format(str(round(x_kde_bandwidth,2))), loc='center', fontsize=plot_note_fontsize)
        plt.tight_layout()

        # Box-Cox transformation of skewed/non-Gaussian variables (https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.boxcox.html).
        #plt.figure(3)
        plt.sca(axs[2])
        df_xt = df_Key.loc[df_Key[column] > 0.0] # Values must be >0.
        xt = df_xt[column].rename("Box-Cox transformation of '{0}'".format(x_name))
        xt, xt_lambda = scipy.stats.boxcox(xt)
        sns.histplot(xt, color=color)
        plt.title("C", loc='left', fontsize=plot_title_fontsize, fontweight='bold')
        xt_n = len(xt)
        plt.xlabel("Frequency distribution of X following Box-Cox transformation")
        plt.title("n = {0}*".format(str(xt_n)), loc='right', fontsize=plot_note_fontsize)
        plt.title("Power parameter (λ) = {0}".format(str(round(xt_lambda,2))), loc='center', fontsize=plot_note_fontsize)
        plt.tight_layout()

        # Kernel smoothing bandwidth: Get kernel density estimate (KDE) bandwidth.
        xt_kde = scipy.stats.gaussian_kde(xt, 'scott')
        xt_f = xt_kde.covariance_factor()
        xt_kde_bandwidth = xt_f * xt.std()

        # Kernel density estimate (KDE) distribution of the Box-Cox-transformed data.
        #plt.figure(4)
        plt.sca(axs[3])
        sns.kdeplot(xt, shade=True, bw_method='scott', color=color)
        plt.title("D", loc='left', fontsize=plot_title_fontsize, fontweight='bold')
        xt_n = len(xt)
        plt.xlabel("Kernel density estimate (KDE) distribution of the Box-Cox-transformed X")
        plt.title("n = {0}*".format(str(xt_n)), loc='right', fontsize=plot_note_fontsize)
        plt.title("KDE bandwidth = {0}".format(str(round(xt_kde_bandwidth,2))), loc='center', fontsize=plot_note_fontsize)
        plt.tight_layout()

        plt.show()
        plt.clf()
        plt.close()

    # If the variable is discrete (ie. categorical), visualize it with a bar chart.
    else:
        # Bar chart (https://seaborn.pydata.org/generated/seaborn.countplot.html).
        sns.countplot(x=x, color=color)
        plt.show()

    ##### Univariate measures.

    # Sample size.
    n = len(x)
    print("\tSample size (n): {0}".format(str(n)))

    # Mean.
    mean = np.mean(x)
    print("\tMean: {0}".format(str(mean)))

    # Median.
    median = np.median(x)
    print("\tMedian: {0}".format(str(median)))

    # Mode.
    modes = scipy.stats.mode(x)
    print("\tMode value: {0} ({1} observations)".format(str(modes.mode[0]), str(modes.count[0])))

    # Range.
    range_min = min(x)
    range_max = max(x)
    print("\tRange: The observed values fall between {0} and {1}".format(str(range_min), str(range_max)))

    # Skewness.
    skewness = scipy.stats.skew(x)
    print("\tSkewness (>0 indicates tail on right): {0}".format(str(skewness)))

    # Kurtosis.
    kurtosis = scipy.stats.kurtosis(x)
    print("\tKurtosis (>0 indicates steep slopes): {0}".format(str(kurtosis)))

    # Standard deviation.
    standard_deviation = np.std(x)
    print("\tStandard deviation: {0}".format(str(standard_deviation)))
    
    # Quartiles.
    quartile_first = np.percentile(x, 25)
    quartile_second = np.percentile(x, 50) # Median
    quartile_third = np.percentile(x, 75)
    IQR = quartile_third - quartile_first
    print("\tQuartiles:\n\t\tFirst quartile (.25), Q1: {0}\n\t\tSecond quartile (.75), Q3: {1}\n\t\tInter quartile range (Q3-Q4), IQR: {2}".format(str(quartile_first),str(quartile_third),str(IQR)))

    # Outliers (https://www.kite.com/python/answers/how-to-remove-outliers-from-a-numpy-array-in-python).
    # Theoretical source: Agresti, A. 2018. Statistical methods for the social sciences. Fith edition, global edition., Boston: Pearson.

    distance_from_mean = abs(x - mean)
    max_deviations = 3
    outlier_condition = distance_from_mean < max_deviations * standard_deviation

    x_outliers_removed = x.where(outlier_condition).dropna()
    x_outliers = x.where(~outlier_condition).dropna()

    x_outliers_right = x_outliers.where(x_outliers > quartile_third).dropna()
    x_outliers_left = x_outliers.where(x_outliers < quartile_first).dropna()

    print("\tOutlier count: {0}".format(str(len(x_outliers))))
    if len(x_outliers_right) > 0:
        print("\tRight outliers:\n\t\tCount: {0}\n\t\tMinimum value: {1}\n\t\tMaximum value: {2}".format(str(len(x_outliers_right)), str(min(x_outliers_right)), str(max(x_outliers_right))))
    if len(x_outliers_left) > 0:
        print("\tLeft outliers:\n\t\tCount: {0}\n\t\tMinimum value: {1}\n\t\tMaximum value: {2}".format(str(len(x_outliers_left)), str(min(x_outliers_left)), str(max(x_outliers_left))))
    
    # Shapiro-Wilk test of normality (https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.shapiro.html).
    def shapiro_wilk(univariate_data, note):
        stat, p = scipy.stats.shapiro(univariate_data)
        #print('stat=%.3f, p=%.3f' % (stat, p))
        if p > 0.05:
            print("\tShapiro-Wilk test of normality ({0}): The variable is probably Gaussian (p={1})".format(note, str(round(p,3))))
        else:
            print("\tShapiro-Wilk test of normality ({0}): The variable is probably NOT Gaussian (p={1})".format(note, str(round(p,3))))

    shapiro_wilk(x, 'including outliers')
    shapiro_wilk(x_outliers_removed, 'outliers excluded')

    print("-------------------------------------------------------")

    # Box plot for distribution (https://seaborn.pydata.org/generated/seaborn.boxplot.html).
    sns.boxplot(x=x, color=color)
    #plt.title("Outliers determined by inter-quartile range", loc='left', fontsize=plot_note_fontsize)
    #plt.title("Mean = {0}".format(str(round(mean,3))), loc='center', fontsize=plot_note_fontsize)
    #plt.title("n = {0}".format(str(len(x))), loc='right', fontsize=plot_note_fontsize)
    plt.xlabel("")
    plt.xticks(fontsize=20)

    plt.show()
    plt.clf()
    plt.close()

univariate('approvalamount', 'Number of vocational students a production unit is approved for', 0.0, color='cornflowerblue')
univariate('currentamount', 'Current number of employed vocational students', 0.0, color='orange')
univariate('propensity', 'Propensity to employ vocational students', 0.0, color='green')













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