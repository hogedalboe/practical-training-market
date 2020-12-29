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
with open(r'C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\PostgreSQL\11. Master data query with names.sql', 'r') as f:
    masterQuery = f.read()

# Get all data of relevance for the descriptive statistical analysis.
df_Master = db.Read(masterQuery)

# Shapiro-Wilk test of normality (https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.shapiro.html).
def shapiro_wilk(univariate_data, note):
    stat, p = scipy.stats.shapiro(univariate_data)
    #print('stat=%.3f, p=%.3f' % (stat, p))
    if p > 0.05:
        print("\tShapiro-Wilk test of normality ({0}): The variable is probably Gaussian (W = {1}, p={2})".format(note, str(round(stat,3)), str(round(p,3)))) # W = the test statistic
    else:
        print("\tShapiro-Wilk test of normality ({0}): The variable is probably NOT Gaussian (W = {1}, p={2})".format(note, str(round(stat,3)), str(round(p,3))))

################################################################################################################################ CSV backup of master data

#df_Master.to_csv(r'C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Master data.csv', index=False, encoding='CP1252')

################################################################################################################################ Determine ratio values between approvals and combined approvals

def approvalRatios():
    df_approvals = db.Read("SELECT * FROM approval")
    df_combinedapprovals = db.Read("SELECT * FROM combinedapproval")

    # Get the ratio between 
    approvalRatio = df_approvals['approvalnumber'].mean() / df_approvals['currentnumber'].mean()
    combinedapprovalRatio = df_combinedapprovals['approvalnumber'].mean() / df_combinedapprovals['currentnumber'].mean()

    print(str(approvalRatio))
    print(str(combinedapprovalRatio))

#approvalRatios()

################################################################################################################################ Univariate shapes of approval/employment/propensity data

df_Key = df_Master[['currentnumber', 'approvalnumber', 'propensity']].dropna()

def univariate(df, column, x_name, countValue, continuous=True, color='blue', plot_note_fontsize=8, plot_title_fontsize=12):
    print("-------------------------------------------------------")

    print("Univariate measures for variable '{0}'".format(x_name))

    # Univariate data.
    x = df[column].rename(x_name)

    # Number of combined approvals with an x value of 'countValue'.
    num_countValue = len(df.loc[df[column] == 0.0].index)
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
        df_xt = df.loc[df[column] > 0.0] # Values must be >0.
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
    print("\tQuartiles:\n\t\tFirst quartile (.25), Q1: {0}\n\t\tSecond quartile (median), Q2: {1}\n\t\tThird quartile (.75), Q3: {2}\n\t\tInter quartile range (Q3-Q4), IQR: {3}".format(str(quartile_first),str(quartile_second),str(quartile_third),str(IQR)))

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
    
    shapiro_wilk(x, 'including outliers')
    shapiro_wilk(x_outliers_removed, 'outliers excluded')

    print("-------------------------------------------------------")

    # Box plot for distribution (https://seaborn.pydata.org/generated/seaborn.boxplot.html).
    boxplot_fontsize = 20
    sns.boxplot(x=x, color=color)
    plt.title("n = {0}".format(str(len(x))), loc='left', fontsize=boxplot_fontsize)
    #plt.title("Range = [{0};{1}]".format(str(range_min),str(range_max)), loc='center', fontsize=boxplot_fontsize)
    #plt.title("Mean = {0}".format(str(mean)), loc='right', fontsize=boxplot_fontsize)
    plt.xlabel("")
    plt.xticks(fontsize=boxplot_fontsize)

    plt.show()
    plt.clf()
    plt.close()

#univariate(df_Key, 'approvalnumber', 'Number of vocational students a production unit is approved for', 0.0, color='cornflowerblue')
#univariate(df_Key, 'currentnumber', 'Current number of employed vocational students', 0.0, color='orange')
#univariate(df_Key, 'propensity', 'Propensity to employ vocational students', 0.0, color='green')

################################################################################################################################ Analyse dichotomous propensity observations

df_Propensity = df_Master.loc[df_Master['propensity'] > 0.0]

def propensity_measures():
    # Mean split
    propensity_mean = np.mean(df_Master['propensity'])
    print("Values less than the mean: " + str(len(df_Propensity[df_Propensity['propensity'] < propensity_mean].index)))
    print("Values equal to or higher than the mean: " + str(len(df_Propensity[df_Propensity['propensity'] >= propensity_mean].index)))

    # Median split
    propensity_median = np.median(df_Master['propensity'])
    print("Values less than the median: " + str(len(df_Propensity[df_Propensity['propensity'] < propensity_median].index)))
    print("Values equal to or higher than the median: " + str(len(df_Propensity[df_Propensity['propensity'] >= propensity_median].index)))

#propensity_measures()

################################################################################################################################ Numbers per education

def education():
    # Sum of propensity within each education.
    df_EducationCurrentNumber = df_Master[['edunum', 'eduname', 'propensity', 'currentnumber']]
    df_EducationCurrentNumber['education_sum_propensity'] = df_EducationCurrentNumber.groupby('edunum')['propensity'].transform('sum')

    # Sum of current numbers of employed students within each education.
    df_EducationCurrentNumber['education_sum_currentnumber'] = df_Master.groupby('edunum')['currentnumber'].transform('sum')
    df_EducationCurrentNumber = df_EducationCurrentNumber.drop_duplicates(subset='eduname', keep="last")
    df_EducationCurrentNumber = df_EducationCurrentNumber.loc[df_EducationCurrentNumber['education_sum_currentnumber'] > 0.0]
    df_EducationCurrentNumber = df_EducationCurrentNumber.sort_values('education_sum_currentnumber', ascending=False)

    # Get the educations with the highest and lowest propensity in relation to currently employed students.
    df_EducationCurrentNumber['CurrentPropensityRatio'] = df_EducationCurrentNumber["education_sum_currentnumber"] / df_EducationCurrentNumber["education_sum_propensity"]
    #df_EducationCurrentNumber = df_EducationCurrentNumber.sort_values('CurrentPropensityRatio', ascending=False)

    # Inspect dataframe
    print(df_EducationCurrentNumber.head(30))

    # Subtract the propensities from the current numbers so that the bars show the correct sums.
    df_EducationCurrentNumber['education_sum_currentnumber_subtracted'] = df_EducationCurrentNumber['education_sum_currentnumber'].sub(df_EducationCurrentNumber['education_sum_propensity'])

    # Prepare dataframe for bar chart.
    df_EducationCurrentNumber = df_EducationCurrentNumber[['eduname', 'education_sum_propensity', 'education_sum_currentnumber_subtracted']]
    df_EducationCurrentNumber['eduname'] = df_EducationCurrentNumber['eduname'].str.slice(0,14)
    df_EducationCurrentNumber.set_index('eduname', inplace=True)

    # Rename columns so that they are comprehensible in the plotted legend.
    df_EducationCurrentNumber = df_EducationCurrentNumber.rename(columns={"education_sum_propensity": "Propensity", "education_sum_currentnumber_subtracted": "Current number"})

    # Bar chart.
    ax = df_EducationCurrentNumber.plot.barh(stacked=True)

    # Add labels
    ax.set_ylabel("", fontsize=14)
    ax.set_xlabel("Current number of employed vocational students", fontsize=18)

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=14)

    plt.legend(prop={'size': 18})

    plt.show()
    plt.clf()
    plt.close()

#education()

################################################################################################################################ Numbers per joint trade committee

def committee():
    # Sum of propensity within each joint trade committee.
    df_EducationCommittee = df_Master[['committeename', 'propensity', 'currentnumber']]
    df_EducationCommittee['committee_sum_propensity'] = df_EducationCommittee.groupby('committeename')['propensity'].transform('sum')

    # Sum of current numbers of employed students within each joint trade committee.
    df_EducationCommittee['committee_sum_currentnumber'] = df_Master.groupby('committeename')['currentnumber'].transform('sum')
    df_EducationCommittee = df_EducationCommittee.drop_duplicates(subset='committeename', keep="last")
    df_EducationCommittee = df_EducationCommittee.loc[df_EducationCommittee['committee_sum_propensity'] > 0.0]
    #df_EducationCommittee = df_EducationCommittee.sort_values('committee_sum_propensity', ascending=False)

    # Get the committees with the highest and lowest propensity in relation to currently employed students.
    df_EducationCommittee['CurrentPropensityRatio'] = df_EducationCommittee["committee_sum_propensity"] / df_EducationCommittee["committee_sum_propensity"]
    df_EducationCommittee = df_EducationCommittee.sort_values('CurrentPropensityRatio', ascending=False)

    # Inspect dataframe
    print(df_EducationCommittee.head(10))

    # Subtract the propensities from the current numbers so that the bars show the correct sums.
    df_EducationCommittee['committee_sum_currentnumber_subtracted'] = df_EducationCommittee['committee_sum_currentnumber'].sub(df_EducationCommittee['committee_sum_propensity'])

    # Prepare dataframe for bar chart.
    df_EducationCommittee = df_EducationCommittee[['committeename', 'committee_sum_propensity', 'committee_sum_currentnumber_subtracted']]
    #df_EducationCommittee['committeename'] = df_EducationCommittee['committeename'].str.slice(0,14)
    df_EducationCommittee.set_index('committeename', inplace=True)

    # Rename columns so that they are comprehensible in the plotted legend.
    df_EducationCommittee = df_EducationCommittee.rename(columns={"committee_sum_propensity": "Propensity", "committee_sum_currentnumber_subtracted": "Current number"})

    # Bar chart.
    propensity = df_EducationCommittee['Propensity'].values.flatten()
    currentnumber = df_EducationCommittee['Current number'].values.flatten()
    ind = np.arange(len(df_EducationCommittee.index))
    width = 0.35

    p1 = plt.bar(ind, propensity, width)
    p2 = plt.bar(ind, currentnumber, width, bottom=propensity)

    plt.ylabel('Current number of employed vocational students')
    plt.xticks(ind, list(df_EducationCommittee.index))
    plt.legend((p1[0], p2[0]), ('Propensity', 'Current number'))

    plt.show()
    plt.clf()
    plt.close()

#committee()

################################################################################################################################ Numbers per sector

def sector():
    # Sum of propensity within each sector.
    df_SectorCurrentNumber = df_Master[['sectorcode', 'sectorname', 'propensity', 'currentnumber']]
    df_SectorCurrentNumber['education_sum_propensity'] = df_SectorCurrentNumber.groupby('sectorcode')['propensity'].transform('sum')

    # Sum of current numbers of employed students within each sector.
    df_SectorCurrentNumber['education_sum_currentnumber'] = df_Master.groupby('sectorcode')['currentnumber'].transform('sum')
    df_SectorCurrentNumber = df_SectorCurrentNumber.drop_duplicates(subset='sectorname', keep="last")
    df_SectorCurrentNumber = df_SectorCurrentNumber.loc[df_SectorCurrentNumber['education_sum_currentnumber'] > 150.0]
    df_SectorCurrentNumber = df_SectorCurrentNumber.sort_values('education_sum_currentnumber', ascending=False)

    # Get the sectors with the highest and lowest propensity in relation to currently employed students.
    df_SectorCurrentNumber['CurrentPropensityRatio'] = df_SectorCurrentNumber["education_sum_currentnumber"] / df_SectorCurrentNumber["education_sum_propensity"]
    #df_SectorCurrentNumber = df_SectorCurrentNumber.sort_values('CurrentPropensityRatio', ascending=False)

    # Inspect dataframe
    print(df_SectorCurrentNumber.head(30))

    # Subtract the propensities from the current numbers so that the bars show the correct sums.
    df_SectorCurrentNumber['education_sum_currentnumber_subtracted'] = df_SectorCurrentNumber['education_sum_currentnumber'].sub(df_SectorCurrentNumber['education_sum_propensity'])

    # Prepare dataframe for bar chart.
    df_SectorCurrentNumber = df_SectorCurrentNumber[['sectorname', 'education_sum_propensity', 'education_sum_currentnumber_subtracted']]
    df_SectorCurrentNumber['sectorname'] = df_SectorCurrentNumber['sectorname'].str.slice(0,80)
    df_SectorCurrentNumber.set_index('sectorname', inplace=True)

    # Rename columns so that they are comprehensible in the plotted legend.
    df_SectorCurrentNumber = df_SectorCurrentNumber.rename(columns={"education_sum_propensity": "Propensity", "education_sum_currentnumber_subtracted": "Current number"})

    # Bar chart
    ax = df_SectorCurrentNumber.plot.barh(stacked=True)

    # Add labels
    ax.set_ylabel("", fontsize=14)
    ax.set_xlabel("Current number of employed vocational students", fontsize=18)

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=14)

    plt.legend(prop={'size': 18})

    #plt.savefig(r'C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\test.png', bbox_inches='tight')

    plt.show()
    plt.clf()
    plt.close()

#sector()

################################################################################################################################ Numbers per business type

def business():
    # Sum of propensity within each joint trade business type.
    df_BusinessCurrentNumber = df_Master[['businesstype', 'propensity', 'currentnumber']]
    df_BusinessCurrentNumber['sum_propensity'] = df_BusinessCurrentNumber.groupby('businesstype')['propensity'].transform('sum')

    # Sum of current numbers of employed students within each joint trade business type.
    df_BusinessCurrentNumber['sum_currentnumber'] = df_Master.groupby('businesstype')['currentnumber'].transform('sum')
    df_BusinessCurrentNumber = df_BusinessCurrentNumber.drop_duplicates(subset='businesstype', keep="last")
    df_BusinessCurrentNumber = df_BusinessCurrentNumber.loc[df_BusinessCurrentNumber['sum_currentnumber'] > 50.0]
    df_BusinessCurrentNumber = df_BusinessCurrentNumber.sort_values('sum_propensity', ascending=False)

    # Get the business type with the highest and lowest propensity in relation to currently employed students.
    df_BusinessCurrentNumber['CurrentPropensityRatio'] = df_BusinessCurrentNumber["sum_propensity"] / df_BusinessCurrentNumber["sum_propensity"]
    df_BusinessCurrentNumber = df_BusinessCurrentNumber.sort_values('sum_currentnumber', ascending=False)

    # Inspect dataframe
    print(df_BusinessCurrentNumber.head(100))

    # Subtract the propensities from the current numbers so that the bars show the correct sums.
    df_BusinessCurrentNumber['sum_currentnumber_subtracted'] = df_BusinessCurrentNumber['sum_currentnumber'].sub(df_BusinessCurrentNumber['sum_propensity'])

    # Prepare dataframe for bar chart.
    df_BusinessCurrentNumber = df_BusinessCurrentNumber[['businesstype', 'sum_propensity', 'sum_currentnumber_subtracted']]
    #df_BusinessCurrentNumber['businesstype'] = df_BusinessCurrentNumber['businesstype'].str.slice(0,14)
    df_BusinessCurrentNumber.set_index('businesstype', inplace=True)

    # Rename columns so that they are comprehensible in the plotted legend.
    df_BusinessCurrentNumber = df_BusinessCurrentNumber.rename(columns={"sum_propensity": "Propensity", "sum_currentnumber_subtracted": "Current number"})

    # Bar chart
    ax = df_BusinessCurrentNumber.plot.barh(stacked=True)

    # Add labels
    ax.set_ylabel("", fontsize=14)
    ax.set_xlabel("Current number of employed vocational students", fontsize=18)

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=14)

    plt.legend(prop={'size': 18})

    plt.savefig(r'C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\test.png', bbox_inches='tight')

    plt.show()
    plt.clf()
    plt.close()

#business()

################################################################################################################################ Average employment numbers for the three largest business types

def averageEmployment():
    df_BusinessCurrentNumber = df_Master[['businesstype', 'currentnumber']]

    # Get individual business types in individual data frames.
    df_Aktieselskab = df_BusinessCurrentNumber.loc[df_BusinessCurrentNumber['businesstype'] == 'Aktieselskab']
    df_Anpartsselskab = df_BusinessCurrentNumber.loc[df_BusinessCurrentNumber['businesstype'] == 'Anpartsselskab']
    df_Enkeltmandsvirksomhed = df_BusinessCurrentNumber.loc[df_BusinessCurrentNumber['businesstype'] == 'Enkeltmandsvirksomhed']

    #### Getting means and standard errors (INCLUDING companies without employed students).
    mean_aktieselskab = df_Aktieselskab["currentnumber"].mean()
    mean_anpartsselskab = df_Anpartsselskab["currentnumber"].mean()
    mean_enkeltmandsvirksomhed = df_Enkeltmandsvirksomhed["currentnumber"].mean()

    print('Mean for aktieselskab (INCLUDING companies without employed students): ' + str(mean_aktieselskab))
    print('Mean for anpartsselskab (INCLUDING companies without employed students): ' + str(mean_anpartsselskab))
    print('Mean for enkeltmandsvirksomhed (INCLUDING companies without employed students): ' + str(mean_enkeltmandsvirksomhed))

    # Getting standard deviations 
    std_aktieselskab = df_Aktieselskab["currentnumber"].std()
    std_anpartsselskab = df_Anpartsselskab["currentnumber"].std()
    std_enkeltmandsvirksomhed = df_Enkeltmandsvirksomhed["currentnumber"].std()

    print('Standard deviation for aktieselskab (INCLUDING companies without employed students): ' + str(std_aktieselskab))
    print('Standard deviation for anpartsselskab (INCLUDING companies without employed students): ' + str(std_anpartsselskab))
    print('Standard deviation for enkeltmandsvirksomhed (INCLUDING companies without employed students): ' + str(std_enkeltmandsvirksomhed))

    #### Excluding production units with currently no employed vocational students.
    df_Aktieselskab_ExcludingZero = df_Aktieselskab.loc[df_Aktieselskab['currentnumber'] > 0.0]["currentnumber"]
    df_Anpartsselskab_ExcludingZero = df_Anpartsselskab.loc[df_Anpartsselskab['currentnumber'] > 0.0]["currentnumber"]
    df_Enkeltmandsvirksomhed_ExcludingZero = df_Enkeltmandsvirksomhed.loc[df_Enkeltmandsvirksomhed['currentnumber'] > 0.0]["currentnumber"]

    # Means.
    mean_aktieselskab_ExcludingZero = df_Aktieselskab_ExcludingZero.mean()
    mean_anpartsselskab_ExcludingZero = df_Anpartsselskab_ExcludingZero.mean()
    mean_enkeltmandsvirksomhed_ExcludingZero = df_Enkeltmandsvirksomhed_ExcludingZero.mean()

    print('Mean for aktieselskab (EXCLUDING companies without employed students): {0} (n={1})'.format(str(mean_aktieselskab_ExcludingZero), len(df_Aktieselskab_ExcludingZero.index)))
    print('Mean for anpartsselskab (EXCLUDING companies without employed students): {0} (n={1})'.format(str(mean_anpartsselskab_ExcludingZero), len(df_Anpartsselskab_ExcludingZero.index)))
    print('Mean for enkeltmandsvirksomhed (EXCLUDING companies without employed students): {0} (n={1})'.format(str(mean_enkeltmandsvirksomhed_ExcludingZero), len(df_Enkeltmandsvirksomhed_ExcludingZero.index)))

    # Getting standard deviations 
    std_aktieselskab_ExcludingZero = df_Aktieselskab.loc[df_Aktieselskab['currentnumber'] > 0.0]["currentnumber"].std()
    std_anpartsselskab_ExcludingZero = df_Anpartsselskab.loc[df_Anpartsselskab['currentnumber'] > 0.0]["currentnumber"].std()
    std_enkeltmandsvirksomhed_ExcludingZero = df_Enkeltmandsvirksomhed.loc[df_Enkeltmandsvirksomhed['currentnumber'] > 0.0]["currentnumber"].std()

    print('Standard deviation for aktieselskab (EXCLUDING companies without employed students): ' + str(std_aktieselskab_ExcludingZero))
    print('Standard deviation for anpartsselskab (EXCLUDING companies without employed students): ' + str(std_anpartsselskab_ExcludingZero))
    print('Standard deviation for enkeltmandsvirksomhed (EXCLUDING companies without employed students): ' + str(std_enkeltmandsvirksomhed_ExcludingZero))

    # Plot bar chart.
    exMeans = (float(mean_aktieselskab_ExcludingZero-mean_aktieselskab), float(mean_anpartsselskab_ExcludingZero-mean_anpartsselskab), float(mean_enkeltmandsvirksomhed_ExcludingZero-mean_enkeltmandsvirksomhed))
    exStd = (float(std_aktieselskab_ExcludingZero), float(std_anpartsselskab_ExcludingZero), float(std_enkeltmandsvirksomhed_ExcludingZero))

    inMeans = (float(mean_aktieselskab), float(mean_anpartsselskab), float(mean_enkeltmandsvirksomhed))
    inStd = (float(std_aktieselskab), float(std_anpartsselskab), float(std_enkeltmandsvirksomhed))

    ind = np.arange(3) # Number of groups.
    width = 0.35 # Bar width.

    p1 = plt.bar(ind, exMeans, width, bottom=inMeans, color='red')
    p2 = plt.bar(ind, inMeans, width, color='gray')

    plt.ylabel('Average number of employed students', fontsize=18)
    plt.xticks(ind, ('Aktieselskab', 'Anpartsselskab', 'Enkeltmandsvirksomhed'), fontsize=16)
    plt.yticks(fontsize=16)
    plt.legend((p1[0], p2[0]), ('Excluding non-employers', 'Including non-employers'), prop={'size': 16})

    plt.show()

#averageEmployment()

################################################################################################################################ Heat map of municipal distribution of employment

def heatMapCurrentNumberAdjusted():

    df_Geography = df_Master[['municipalitycode', 'municipalityname', 'regioncode', 'currentnumber', 'approvalnumber', 'regionpopulation', 'municipalitypopulation']]

    # Sum values by municipality.
    df_GeographyMunicipality = df_Geography.groupby(['municipalitycode'], as_index=False)[['currentnumber', 'approvalnumber']].sum()
    df_GeographyMunicipality = df_Geography[['municipalitycode', 'municipalitypopulation']].merge(df_GeographyMunicipality, how='left', left_on='municipalitycode', right_on='municipalitycode')
    df_GeographyMunicipality = df_GeographyMunicipality.drop_duplicates()

    # Values per x municipal inhabitants.
    df_GeographyMunicipality['currentnumber_per_x_municipal_inhabitants'] = (df_GeographyMunicipality['currentnumber'] / df_GeographyMunicipality['municipalitypopulation'])*10000

    # Merge with the remaining municipalities in the database (not represented in the approval data).
    df_GeographyMunicipality = db.Read("""SELECT municipality.municipalitycode, 
        municipalitydemographics.population as municipalitypopulation, 
        municipality.name as municipalityname
            FROM municipality 
                JOIN municipalitydemographics 
                    ON municipalitydemographics.municipalitycode = municipality.municipalitycode""").merge(df_GeographyMunicipality, how='left', left_on='municipalitycode', right_on='municipalitycode')

    # Clean up the merged dataframe.
    df_GeographyMunicipality = df_GeographyMunicipality.fillna(0)
    df_GeographyMunicipality = df_GeographyMunicipality.drop('municipalitypopulation_y', 1)

    print(df_GeographyMunicipality.sort_values('currentnumber_per_x_municipal_inhabitants', ascending=True).head(100))

    print("Average municipal population size: " + str(float(db.Read('SELECT AVG(population) FROM municipalitydemographics WHERE yearofmeasurement = 2018')['avg'][0])))

    # Heat map: Color scale.
    colorScale = hm.dict_ColorScales['currentnumber']

    # Heat map: Determine 'heat' of municipality.
    dict_HeatMap = {}
    for i, row in df_GeographyMunicipality.iterrows():
        for key, color in colorScale.items():
            if row['currentnumber_per_x_municipal_inhabitants'] >= key:
                dict_HeatMap['0'+str(int(row['municipalitycode']))] = color

    # Create heat map.
    hm.GeographicalVisualizer(dict_SubnationalColor=dict_HeatMap, 
        path_Shapefile='KOMMUNE.shp', 
        sf_SubnationalColumn='KOMKODE', 
        dict_ColorScale=colorScale).plot_map('Current number of students per 10000 municipal inhabitants.png', 
            scaleTextBefore='>= ', 
            scaleTextAfter='', 
            scaleTextAdjustLeft=25000
        )

#heatMapCurrentNumberAdjusted()

def heatMapCurrentNumberUnadjusted():

    df_Geography = df_Master[['municipalitycode', 'municipalityname', 'currentnumber']]

    # Sum values by municipality.
    df_GeographyMunicipality = df_Geography.groupby(['municipalitycode'], as_index=False)[['currentnumber']].sum()
    df_GeographyMunicipality = df_Geography[['municipalitycode']].merge(df_GeographyMunicipality, how='left', left_on='municipalitycode', right_on='municipalitycode')
    df_GeographyMunicipality = df_GeographyMunicipality.drop_duplicates()

    # Merge with the remaining municipalities in the database (not represented in the approval data).
    df_GeographyMunicipality = db.Read("""SELECT municipality.municipalitycode, 
        municipality.name as municipalityname
            FROM municipality 
                JOIN municipalitydemographics 
                    ON municipalitydemographics.municipalitycode = municipality.municipalitycode""").merge(df_GeographyMunicipality, how='left', left_on='municipalitycode', right_on='municipalitycode')

    # Clean up the merged dataframe.
    df_GeographyMunicipality = df_GeographyMunicipality.fillna(0)

    print(df_GeographyMunicipality.sort_values('currentnumber', ascending=True).head(100))

    # Heat map: Color scale.
    colorScale = hm.dict_ColorScales['currentnumberUnadjusted']

    # Heat map: Determine 'heat' of municipality.
    dict_HeatMap = {}
    for i, row in df_GeographyMunicipality.iterrows():
        for key, color in colorScale.items():
            if row['currentnumber'] >= key:
                dict_HeatMap['0'+str(int(row['municipalitycode']))] = color

    # Create heat map.
    hm.GeographicalVisualizer(dict_SubnationalColor=dict_HeatMap, 
        path_Shapefile='KOMMUNE.shp', 
        sf_SubnationalColumn='KOMKODE', 
        dict_ColorScale=colorScale).plot_map('Current number of students per municipality (unadjusted).png', 
            scaleTextBefore='>= ', 
            scaleTextAfter='', 
            scaleTextAdjustLeft=25000
        )

#heatMapCurrentNumberUnadjusted()

################################################################################################################################ Heat map of municipal distribution of propensity

def heatMapPropensity():

    df_Geography = df_Master[['municipalitycode', 'municipalityname', 'regioncode', 'currentnumber', 'approvalnumber', 'regionpopulation', 'municipalitypopulation']]

    # Sum values by municipality.
    df_GeographyMunicipality = df_Geography.groupby(['municipalitycode'], as_index=False)[['currentnumber', 'approvalnumber']].sum()
    df_GeographyMunicipality = df_Geography[['municipalitycode', 'municipalitypopulation']].merge(df_GeographyMunicipality, how='left', left_on='municipalitycode', right_on='municipalitycode')
    df_GeographyMunicipality = df_GeographyMunicipality.drop_duplicates()

    # Municipal propensity: The ratio of municipalities accumulated approval numbers and accumulated numbers of currently employed vocational students.
    df_GeographyMunicipality['accumulated_propensity'] = df_GeographyMunicipality['currentnumber'] / df_GeographyMunicipality['approvalnumber']

    # Merge with the remaining municipalities in the database (not represented in the approval data).
    df_GeographyMunicipality = db.Read("""SELECT municipality.municipalitycode, 
        municipalitydemographics.population as municipalitypopulation, 
        municipality.name as municipalityname
            FROM municipality 
                JOIN municipalitydemographics 
                    ON municipalitydemographics.municipalitycode = municipality.municipalitycode""").merge(df_GeographyMunicipality, how='left', left_on='municipalitycode', right_on='municipalitycode')

    # Clean up the merged dataframe.
    df_GeographyMunicipality = df_GeographyMunicipality.fillna(0)
    df_GeographyMunicipality = df_GeographyMunicipality.drop('municipalitypopulation_y', 1)

    print(df_GeographyMunicipality.sort_values('accumulated_propensity', ascending=True).head(100))

    print("Average municipal population size: " + str(float(db.Read('SELECT AVG(population) FROM municipalitydemographics WHERE yearofmeasurement = 2018')['avg'][0])))

    # Heat map: Color scale.
    colorScale = hm.dict_ColorScales['propensity']

    # Heat map: Determine 'heat' of municipality.
    dict_HeatMap = {}
    for i, row in df_GeographyMunicipality.iterrows():
        for key, color in colorScale.items():
            if row['accumulated_propensity'] >= key:
                dict_HeatMap['0'+str(int(row['municipalitycode']))] = color

    # Create heat map.
    hm.GeographicalVisualizer(dict_SubnationalColor=dict_HeatMap, 
        path_Shapefile='KOMMUNE.shp', 
        sf_SubnationalColumn='KOMKODE', 
        dict_ColorScale=colorScale).plot_map('Municipal propensity to utilize approvals.png', 
            scaleTextBefore='>= ', 
            scaleTextAfter='', 
            scaleTextAdjustLeft=25000
        )

#heatMapPropensity()

################################################################################################################################ Regional propensity and adjusted number of currently employed students

def RegionCurrentNumberAdjusted():

    df_Geography = df_Master[['regioncode', 'regionname', 'currentnumber', 'approvalnumber', 'regionpopulation']]

    # Sum values by region.
    df_GeographyRegion = df_Geography.groupby(['regioncode'], as_index=False)[['currentnumber', 'approvalnumber', 'regionname']].sum()
    df_GeographyRegion = df_Geography[['regioncode', 'regionpopulation', 'regionname']].merge(df_GeographyRegion, how='left', left_on='regioncode', right_on='regioncode')
    df_GeographyRegion = df_GeographyRegion.drop_duplicates()

    # Values per x regional inhabitants.
    df_GeographyRegion['Current number (adjusted)'] = (df_GeographyRegion['currentnumber'] / df_GeographyRegion['regionpopulation'])*500000

    # Calculate regional propensities.
    df_GeographyRegion['propensity'] = df_GeographyRegion['currentnumber'] / df_GeographyRegion['approvalnumber']

    # Calculate means and standard deviations of the current numbers within the regions.
    df_MeanStd = df_Geography[['regioncode', 'regionname', 'currentnumber']].groupby('regioncode', as_index=False).agg([np.mean, np.std])
    df_GeographyRegion = df_MeanStd.merge(df_GeographyRegion, how='left', left_on='regioncode', right_on='regioncode')

    df_GeographyRegion = df_GeographyRegion.sort_values('Current number (adjusted)', ascending=True)

    # Inspect dataframe.
    print(df_GeographyRegion.sort_values('Current number (adjusted)', ascending=True).head(7))

    # Bar chart.
    ax = df_GeographyRegion[['regionname', 'Current number (adjusted)']].plot.barh(color='green', legend=False, alpha=0.5)
    ax.set_yticklabels(df_GeographyRegion['regionname'])
    ax.set_xlabel("Number of employed students per 500K inhabitants", fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=16, rotation=45)

    plt.savefig(r'C:\Users\hoged\OneDrive\Skrivebord\test.png', bbox_inches='tight')

    #plt.show()
    plt.clf()
    plt.close()

#RegionCurrentNumberAdjusted()

################################################################################################################################ Commuting per municipality

def heatmapCommuting():
    # Get commuting figures in km from the database.
    df_Commuting = db.Read("SELECT municipalitycode, avgcommutekm FROM municipalitydemographics WHERE yearofmeasurement = 2018")

    # Heat map: Color scale.
    colorScale = hm.dict_ColorScales['commuting']

    # Heat map: Determine 'heat' of municipality.
    dict_HeatMap = {}
    for i, row in df_Commuting.iterrows():
        for key, color in colorScale.items():
            if row['avgcommutekm'] >= key:
                dict_HeatMap['0'+str(int(row['municipalitycode']))] = color

    # Create heat map.
    hm.GeographicalVisualizer(dict_SubnationalColor=dict_HeatMap, 
        path_Shapefile='KOMMUNE.shp', 
        sf_SubnationalColumn='KOMKODE', 
        dict_ColorScale=colorScale).plot_map('Average commuting distance in kilometres per municipality.png', 
            scaleTextBefore='> ', 
            scaleTextAfter=' km', 
            scaleTextAdjustLeft=25000
        )

#heatmapCommuting()

################################################################################################################################ Scatterplot: Commuting and student numbers per municipality

def scatterplotCommuting():
    df_Commuting = db.Read("SELECT municipalitycode, avgcommutekm, population FROM municipalitydemographics")
    df_MunicipalNumbers = df_Master[['municipalitycode', 'currentnumber', 'approvalnumber']]

    # Sum values by municipalities and merge with commuting data.
    df_MunicipalNumbers = df_MunicipalNumbers.groupby(['municipalitycode'], as_index=False)[['currentnumber', 'approvalnumber']].sum()
    df_MunicipalNumbers = df_Commuting.merge(df_MunicipalNumbers, how='left', left_on='municipalitycode', right_on='municipalitycode')

    # Municipal propensity: The ratio of municipalities accumulated approval numbers and accumulated numbers of currently employed vocational students.
    df_MunicipalNumbers['propensity'] = df_MunicipalNumbers['currentnumber'] / df_MunicipalNumbers['approvalnumber']

    # Adjust current number for municipal population size.
    df_MunicipalNumbers['Current number (adjusted)'] = (df_MunicipalNumbers['currentnumber'] / df_MunicipalNumbers['population'])*10000

    # Remove observations with zero values.
    df_MunicipalNumbers = df_MunicipalNumbers[df_MunicipalNumbers['Current number (adjusted)'] > 0.0]
    df_MunicipalNumbers = df_MunicipalNumbers.fillna(0)

    print(df_MunicipalNumbers.sort_values('Current number (adjusted)', ascending=True).head(100))

    # Regression.
    x = df_MunicipalNumbers['avgcommutekm']
    y = df_MunicipalNumbers['Current number (adjusted)']
    slope, intercept, rvalue, pvalue, stderr = scipy.stats.linregress(x, y)
    regressionLabel = f'Regression line:\ny={intercept:.2f}+{slope:.2f}x\nr={rvalue:.2f}\np={pvalue:.2f}'

    # Scatter plot with regression line.
    fig, ax = plt.subplots()

    ax.plot(x, y, linewidth=0, marker='s')
    ax.plot(x, intercept + slope * x, label=regressionLabel)

    ax.set_xlabel('Average commute in kilometers', fontsize=16)
    ax.set_ylabel('Number of currently employed vocational\nstudents per 10,000 municipal inhabitants', fontsize=16)
    ax.legend(facecolor='white', fontsize=14)

    plt.show()
    plt.clf()
    plt.close()

#scatterplotCommuting()

################################################################################################################################ Scatterplot and heat map for average distances to nearest school faility per municipality

def proximity():
    df_MunicipalNumbers = df_Master[['municipalitycode', 'currentnumber', 'approvalnumber', 'nearestfacilitykm']]

    # Get number of observations per municipality.
    df_MunicipalObservations = df_MunicipalNumbers.groupby(['municipalitycode'], as_index=False).size().reset_index(name='n')

    # Get approval and employment numbers per municipality.
    df_MunicipalNumbers = df_MunicipalNumbers.groupby(['municipalitycode'], as_index=False).sum()

    # Merge with number of obersvations and remaining municipalities in the database.
    df_MunicipalNumbers = df_MunicipalObservations.merge(df_MunicipalNumbers, how='left', left_on='municipalitycode', right_on='municipalitycode')
    df_MunicipalNumbers = db.Read("SELECT municipalitycode, name FROM municipality").merge(df_MunicipalNumbers, how='left', left_on='municipalitycode', right_on='municipalitycode')

    # Get average distance to nearest school facility per municipality.
    avg_distance = "Average distance to nearest school facility (km)"
    df_MunicipalNumbers[avg_distance] = df_MunicipalNumbers['nearestfacilitykm'] / df_MunicipalNumbers['n']

    # Clean up dataframe.
    df_MunicipalNumbers = df_MunicipalNumbers.fillna(0)
    df_MunicipalNumbers = df_MunicipalNumbers.drop('n', 1)

    print(df_MunicipalNumbers.sort_values(avg_distance, ascending=True).head(100))

    # Heat map: Color scale.
    colorScale = hm.dict_ColorScales['distance']

    # Heat map: Determine 'heat' of municipality.
    dict_HeatMap = {}
    for i, row in df_MunicipalNumbers.iterrows():
        for key, color in colorScale.items():
            if row[avg_distance] > key:
                dict_HeatMap['0'+str(int(row['municipalitycode']))] = color

    # Create heat map.
    hm.GeographicalVisualizer(dict_SubnationalColor=dict_HeatMap, 
        path_Shapefile='KOMMUNE.shp', 
        sf_SubnationalColumn='KOMKODE', 
        dict_ColorScale=colorScale).plot_map('Average distance (km) to nearest school facility per municipality.png', 
            scaleTextBefore='> ', 
            scaleTextAfter=' km', 
            scaleTextAdjustLeft=25000
        )

    # Merge with municipal population sizes.
    df_MunicipalPopulation = db.Read("SELECT municipalitycode, population FROM municipalitydemographics")
    df_MunicipalNumbers = df_MunicipalNumbers.merge(df_MunicipalPopulation, how='left', left_on='municipalitycode', right_on='municipalitycode')

    # Remove observations with no currently employed students, missing population data and missing distance data.
    df_MunicipalNumbers = df_MunicipalNumbers.loc[(df_MunicipalNumbers[avg_distance] > 0.0) & (df_MunicipalNumbers['currentnumber'] > 0.0) & (df_MunicipalNumbers['population'] > 0.0)]

    ### Regression and scatterplot including outliers.

    # Regression.
    x = df_MunicipalNumbers['population']
    y = df_MunicipalNumbers[avg_distance]
    slope, intercept, rvalue, pvalue, stderr = scipy.stats.linregress(x, y)
    regressionLabel = f'Regression line:\ny={intercept:.2f}+{slope:.2f}x\nr={rvalue:.2f}\np={pvalue:.2f}'

    # Testing for normality (outliers INCLUDED).
    shapiro_wilk(x, 'Population sizes including outliers')
    shapiro_wilk(y, 'Distances including outliers')

    # Scatter plot with regression line.
    fig, ax = plt.subplots()

    ax.plot(x, y, linewidth=0, marker='s')
    ax.plot(x, intercept + slope * x, label=regressionLabel)

    ax.set_xlabel('Municipal population size', fontsize=16)
    ax.set_ylabel('Average distance to nearest school facility (km)', fontsize=16)
    ax.legend(facecolor='white', fontsize=14)

    plt.show()
    plt.clf()
    plt.close()

    ### Regression and scatterplot excluding outliers.

    # Excluding outliers.
    df_MunicipalNumbers = df_MunicipalNumbers.loc[(df_MunicipalNumbers[avg_distance] < 100) & (df_MunicipalNumbers['population'] < 200000)]

    # Regression.
    x = df_MunicipalNumbers['population']
    y = df_MunicipalNumbers[avg_distance]
    slope, intercept, rvalue, pvalue, stderr = scipy.stats.linregress(x, y)
    regressionLabel = f'Regression line:\ny={intercept:.2f}+{slope:.2f}x\nr={rvalue:.2f}\np={pvalue:.2f}'

    # Testing for normality (outliers EXCLUDED).
    shapiro_wilk(x, 'Population sizes excluding outliers')
    shapiro_wilk(y, 'Distances excluding outliers')

    # Scatter plot with regression line.
    fig, ax = plt.subplots()

    ax.plot(x, y, linewidth=0, marker='s')
    ax.plot(x, intercept + slope * x, label=regressionLabel)

    ax.set_xlabel('Municipal population size', fontsize=16)
    ax.set_ylabel('Average distance to nearest school facility (km)', fontsize=16)
    ax.legend(facecolor='white', fontsize=14)

    plt.show()
    plt.clf()
    plt.close()

    ### Visually inspect distributions for the variables excluding outliers.
    sns.distplot(x, kde=True)
    plt.xlabel('Municipal population size', fontsize=16)

    plt.show()
    plt.clf()
    plt.close()

#proximity()

################################################################################################################################ Employment rate

def employmentRate():

    df_MunicipalNumbers = df_Master[['municipalitycode', 'currentnumber', 'approvalnumber']]

    # Get approval and employment numbers per municipality.
    df_MunicipalNumbers = df_MunicipalNumbers.groupby(['municipalitycode'], as_index=False).sum()

    # Merge with municipal employment rates.
    df_MunicipalEmployment = db.Read("SELECT municipalitycode, employmentrate, population FROM municipalitydemographics WHERE yearofmeasurement = 2018")
    df_MunicipalNumbers = df_MunicipalEmployment.merge(df_MunicipalNumbers, how='left', left_on='municipalitycode', right_on='municipalitycode')

    # Values per x municipal inhabitants.
    df_MunicipalNumbers['adjusted_currentnumber'] = (df_MunicipalNumbers['currentnumber'] / df_MunicipalNumbers['population'])*10000

    # Heat map: Color scale.
    colorScale = hm.dict_ColorScales['employmentrate']

    # Heat map: Determine 'heat' of municipality.
    dict_HeatMap = {}
    for i, row in df_MunicipalNumbers.iterrows():
        for key, color in colorScale.items():
            if row['employmentrate'] > key:
                dict_HeatMap['0'+str(int(row['municipalitycode']))] = color

    # Create heat map.
    hm.GeographicalVisualizer(dict_SubnationalColor=dict_HeatMap, 
        path_Shapefile='KOMMUNE.shp', 
        sf_SubnationalColumn='KOMKODE', 
        dict_ColorScale=colorScale).plot_map('Employment rate per municipality.png', 
            scaleTextBefore='> ', 
            scaleTextAfter=' ', 
            scaleTextAdjustLeft=25000
        )

    # Clean up dataframe.
    df_MunicipalNumbers = df_MunicipalNumbers.fillna(0)
    df_MunicipalNumbers = df_MunicipalNumbers.loc[(df_MunicipalNumbers['currentnumber'] > 0.0)]

    print(df_MunicipalNumbers.sort_values('employmentrate', ascending=True).head(100))

    # Regression.
    x = df_MunicipalNumbers['employmentrate']
    y = df_MunicipalNumbers['adjusted_currentnumber']
    slope, intercept, rvalue, pvalue, stderr = scipy.stats.linregress(x, y)
    regressionLabel = f'Regression line:\ny={intercept:.2f}+{slope:.2f}x\nr={rvalue:.2f}\np={pvalue:.2f}'

    # Testing for normality (outliers EXCLUDED).
    shapiro_wilk(x, 'Employment rate')
    shapiro_wilk(y, 'Adjusted current number')

    # Scatter plot with regression line.
    fig, ax = plt.subplots()

    ax.plot(x, y, linewidth=0, marker='s')
    ax.plot(x, intercept + slope * x, label=regressionLabel)

    ax.set_xlabel('Municipal employment rate', fontsize=16)
    ax.set_ylabel('Number of currently employed vocational students per 10,000 municipal inhabitants', fontsize=16)
    ax.legend(facecolor='white', fontsize=14)

    plt.show()
    plt.clf()
    plt.close()

#employmentRate()

################################################################################################################################ Disposable income

def disposableIncome():
    df_MunicipalNumbers = df_Master[['municipalitycode', 'currentnumber', 'approvalnumber']]

    # Get approval and employment numbers per municipality.
    df_MunicipalNumbers = df_MunicipalNumbers.groupby(['municipalitycode'], as_index=False).sum()

    # Merge with municipal employment rates.
    df_MunicipalIncome = db.Read("SELECT municipalitycode, yearlydisposableincome, population FROM municipalitydemographics WHERE yearofmeasurement = 2018")
    df_MunicipalNumbers = df_MunicipalIncome.merge(df_MunicipalNumbers, how='left', left_on='municipalitycode', right_on='municipalitycode')

    # Values per x municipal inhabitants.
    df_MunicipalNumbers['adjusted_currentnumber'] = (df_MunicipalNumbers['currentnumber'] / df_MunicipalNumbers['population'])*10000

    print(df_MunicipalNumbers.sort_values('yearlydisposableincome', ascending=True).head(100))

    # Heat map: Color scale.
    colorScale = hm.dict_ColorScales['yearlydisposableincome']

    # Heat map: Determine 'heat' of municipality.
    dict_HeatMap = {}
    for i, row in df_MunicipalNumbers.iterrows():
        for key, color in colorScale.items():
            if row['yearlydisposableincome'] > key:
                dict_HeatMap['0'+str(int(row['municipalitycode']))] = color

    # Create heat map.
    hm.GeographicalVisualizer(dict_SubnationalColor=dict_HeatMap, 
        path_Shapefile='KOMMUNE.shp', 
        sf_SubnationalColumn='KOMKODE', 
        dict_ColorScale=colorScale).plot_map('Average yearly disposable income per municipality.png', 
            scaleTextBefore='> DKK', 
            scaleTextAfter='', 
            scaleTextAdjustLeft=50000
        )

#disposableIncome()

################################################################################################################################ Financial figures and company attributes

def financials():
    df_Finance = df_Master[['currentnumber', 'approvalnumber', 'netturnover', 'netresult', 'liquidityratio', 'roi', 'solvencyratio', 'established', 'employees']]

    # Remove observations with missing data.
    df_Finance = df_Finance.fillna(0)

    print("n = " + str(len(df_Finance.index)))

    # Net turnover.
    df = df_Finance.loc[(df_Finance['netturnover'] > 0.0)]
    univariate(df, 'netturnover', 'Net turnover', 0.0, color='purple')

    # Net result.
    df = df_Finance.loc[(df_Finance['netresult'] != 0)]
    univariate(df, 'netresult', 'Net result', 0.0, color='black')

    # Liquidity ratio.
    df = df_Finance.loc[(df_Finance['liquidityratio'] != 0)]
    univariate(df, 'liquidityratio', 'Liquidity ratio', 0.0, color='black')

    # Return-on-investment, ROI.
    df = df_Finance.loc[(df_Finance['roi'] != 0)]
    univariate(df, 'roi', 'Return-on-investment, ROI', 0.0, color='black')

    # Solvency ratio.
    df = df_Finance.loc[(df_Finance['solvencyratio'] != 0)]
    univariate(df, 'solvencyratio', 'Solvency ratio', 0.0, color='black')

    # Year of establishment.
    df = df_Finance.loc[(df_Finance['established'] != 0)]
    univariate(df, 'established', 'Year of establishment', 0.0, color='black')

    # Histogram for year of establishment.
    sns.histplot(df['established'], color='black')
    x_n = len(df['established'].index)
    plt.title("n = {}".format(str(x_n)), loc='right')
    plt.xlabel("{0}".format('Year of establishment'))
    plt.tight_layout()
    plt.show()
    plt.clf()
    plt.close()

    # Total number of employees.
    df = df_Finance.loc[(df_Finance['employees'] != 0)]
    univariate(df, 'employees', 'Total number of employees', 0.0, color='black')

    # Histogram for total number of employees.
    sns.histplot(df['employees'], color='black')
    x_n = len(df['employees'].index)
    plt.title("n = {}".format(str(x_n)), loc='right')
    plt.xlabel("{0}".format('Total number of employees'))
    plt.tight_layout()
    plt.show()
    plt.clf()
    plt.close()

#financials()

################################################################################################################################ Disconnect database

db.Disconnect()