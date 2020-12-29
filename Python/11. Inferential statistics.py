import config
import objects

import matplotlib.pyplot as plt
import seaborn as sns
import pandas
import numpy as np 
import scipy.stats
from scipy.stats import shapiro
import statsmodels.api as sm
from scipy.stats import kruskal

db = objects.Database(config.server, config.database, config.user, config.password)

# Get query for obtaining master data.
masterQuery = ""
with open(r'C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\PostgreSQL\11. Master data query with names.sql', 'r') as f:
    masterQuery = f.read()

# Get all data of relevance for the descriptive statistical analysis.
df_Master = db.Read(masterQuery)

############################################################################################################################################### Methods.

# Shapiro-Wilk test of normality (https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.shapiro.html).
def shapiro_wilk(univariate_data, note):
    stat, p = scipy.stats.shapiro(univariate_data)
    #print('stat=%.3f, p=%.3f' % (stat, p))
    if p > 0.05:
        print("\tShapiro-Wilk test of normality ({0}): The variable is probably Gaussian (W = {1}, p={2})".format(note, str(round(stat,3)), str(round(p,3)))) # W = the test statistic
    else:
        print("\tShapiro-Wilk test of normality ({0}): The variable is probably NOT Gaussian (W = {1}, p={2})".format(note, str(round(stat,3)), str(round(p,3))))

# Logistisk regression (https://www.geeksforgeeks.org/logistic-regression-using-statsmodels/).
# Documentation: https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.Logit.html
def logreg(y, x):
    log_reg = sm.Logit(y, x).fit() 
    print(log_reg.summary())
    input('Press any key to continue...')

# Kruskal-Wallis H test (https://machinelearningmastery.com/statistical-hypothesis-tests-in-python-cheat-sheet/).
# Documentation: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html 
def interpret_kruskal(stat, p):
    print('H=%.3f, p=%.3f' % (stat, p))
    if p > 0.05:
        print('Accept NULL hypothesis - No significant difference between groups.')
    else:
        print('Reject NULL hypothesis - Significant differences exist between groups.')
    input('Press any key to continue...')

############################################################################################################################################### Section 5.4.2 (Company attributes and implications of missing data).

def missing():
    df = df_Master[['currentnumber', 'approvalnumber', 'propensity', 'netresult', 'established', 'employees']]

    # Defining the independent variables .
    x = df[['currentnumber', 'approvalnumber', 'propensity']] 
    
    # Creating dummy (dependent) variables.
    df.loc[~df['employees'].isnull(), 'dummy_employees'] = 1
    df.loc[df['employees'].isnull(), 'dummy_employees'] = 0

    df.loc[~df['established'].isnull(), 'dummy_established'] = 1
    df.loc[df['established'].isnull(), 'dummy_established'] = 0

    df.loc[~df['netresult'].isnull(), 'dummy_netresult'] = 1
    df.loc[df['netresult'].isnull(), 'dummy_netresult'] = 0

    # Running logistic regression model with dependent variables individually.
    logreg(df[['dummy_employees']] , x)
    logreg(df[['dummy_established']] , x)
    logreg(df[['dummy_netresult']] , x)

#missing()

def businessType():
    df = df_Master[['currentnumber', 'approvalnumber', 'propensity', 'businesstype']]

    # Remove observations where business type is not either sole proprietorship or public/private limited.
    df = df.loc[(df['businesstype'] == 'Aktieselskab') | (df['businesstype'] == 'Anpartsselskab') | (df['businesstype'] == 'Enkeltmandsvirksomhed')]

    # Defining the independent variables .
    x = df[['currentnumber', 'approvalnumber', 'propensity']] 

    # Creating dummy (dependent) variables.
    df.loc[df['businesstype'] == 'Aktieselskab', 'publiclimited'] = 1
    df.loc[df['businesstype'] != 'Aktieselskab', 'publiclimited'] = 0

    df.loc[(df['businesstype'] == 'Aktieselskab') | (df['businesstype'] == 'Anpartsselskab'), 'publicprivatelimited'] = 1
    df.loc[(df['businesstype'] != 'Aktieselskab') & (df['businesstype'] != 'Anpartsselskab'), 'publicprivatelimited'] = 0

    # Running logistic regression model with dependent variables individually.
    logreg(df[['publiclimited']] , x)
    logreg(df[['publicprivatelimited']] , x)

#businessType()

def businessSector():
    df = df_Master[['currentnumber', 'approvalnumber', 'propensity', 'sectorcode', 'sectorname']]

    # Sector codes.
    sectorcode_frem = 251100
    sectorcode_maskin = 256200
    sectorcode_auto = 452010
    sectorcode_detail = 451120

    # Limit to the four most represented business sectors.
    df = df.loc[(df['sectorcode'] == sectorcode_frem) | (df['sectorcode'] == sectorcode_maskin) | (df['sectorcode'] == sectorcode_auto) | (df['sectorcode'] == sectorcode_detail)]

    # Analyse variance in currentnumber across sectors.
    stat, p = kruskal(*[group["currentnumber"].values for name, group in df.groupby("sectorcode")])
    interpret_kruskal(stat, p)

    # Analyse variance in propensity across sectors.
    stat, p = kruskal(*[group["propensity"].values for name, group in df.groupby("sectorcode")])
    interpret_kruskal(stat, p)

#businessSector()

############################################################################################################################################### Section 5.4.3 (The influences of financial figures and school proximity).

def finance():
    df = df_Master[['currentnumber', 'propensity', 'netresult', 'roi', 'nearestfacilitykm']]
    df = df.dropna()

    # Defining the independent variables .
    x = df[['netresult', 'roi', 'nearestfacilitykm']] 

    # Creating dummy (dependent) variables (that do not require further omissions).
    df.loc[(df['currentnumber'] > 0), 'employs_any'] = 1
    df.loc[(df['currentnumber'] == 0), 'employs_any'] = 0

    df.loc[(df['propensity'] >= 0.337), 'high_propensity'] = 1
    df.loc[(df['propensity'] < 0.337), 'high_propensity'] = 0

    print(df.head(10))

    # Running logistic regression model with dependent variables individually.
    logreg(df[['employs_any']] , x)
    logreg(df[['high_propensity']] , x)

    # Remove observation with zero employed vocational students.
    df = df.loc[df['currentnumber'] > 0]

    # Redefining the independent variables .
    x = df[['netresult', 'roi', 'nearestfacilitykm']] 

    # Creating dummy (dependent) variable..
    df.loc[(df['currentnumber'] > 1), 'employs_several'] = 1
    df.loc[(df['currentnumber'] == 1), 'employs_several'] = 0

    print(df.head(10))

    logreg(df[['employs_several']] , x)

#finance()

############################################################################################################################################### Section 5.4.4 (Subnational variance).

def subnational():
    df = df_Master[['currentnumber', 'propensity', 'regioncode', 'municipalitycode']]

    # Analyse variance across regions.
    print('Region: Current number')
    stat, p = kruskal(*[group["currentnumber"].values for name, group in df.groupby("regioncode")])
    interpret_kruskal(stat, p)

    print('Region: Propensity')
    stat, p = kruskal(*[group["propensity"].values for name, group in df.groupby("regioncode")])
    interpret_kruskal(stat, p)

    # Analyse variance across municipalities.
    print('Municipality: Current number')
    stat, p = kruskal(*[group["currentnumber"].values for name, group in df.groupby("municipalitycode")])
    interpret_kruskal(stat, p)

    print('Municipality: Propensity')
    stat, p = kruskal(*[group["propensity"].values for name, group in df.groupby("municipalitycode")])
    interpret_kruskal(stat, p)

    # Remove the capital region and test again.
    df = df.loc[(df['regioncode'] != 1084)]

    print('Region (excluding capital): Current number')
    stat, p = kruskal(*[group["currentnumber"].values for name, group in df.groupby("regioncode")])
    interpret_kruskal(stat, p)

    print('Region (excluding capital): Propensity')
    stat, p = kruskal(*[group["propensity"].values for name, group in df.groupby("regioncode")])
    interpret_kruskal(stat, p)

#subnational()

############################################################################################################################################### Section 5.4.5 (Demographical correlations).

def demographics():
    df = df_Master[['currentnumber', 'propensity', 'yearlydisposableincome', 'employmentrate', 'employmentavailabilityrate', 'avgcommutekm']]
    df = df.dropna()

    # Defining the independent variables.
    x = df[['yearlydisposableincome', 'employmentrate', 'employmentavailabilityrate', 'avgcommutekm']] 

    # Creating dummy (dependent) variables (that do not require further omissions).
    df.loc[(df['currentnumber'] > 0), 'employs_any'] = 1
    df.loc[(df['currentnumber'] == 0), 'employs_any'] = 0

    df.loc[(df['propensity'] >= 0.337), 'high_propensity'] = 1
    df.loc[(df['propensity'] < 0.337), 'high_propensity'] = 0

    # Running logistic regression model with dependent variables individually.
    logreg(df[['employs_any']] , x)
    logreg(df[['high_propensity']] , x)

    # Remove observation with zero employed vocational students.
    df = df.loc[df['currentnumber'] > 0]

    # Redefining the independent variables .
    x = df[['yearlydisposableincome', 'employmentrate', 'employmentavailabilityrate', 'avgcommutekm']] 

    # Creating dummy (dependent) variable..
    df.loc[(df['currentnumber'] > 1), 'employs_several'] = 1
    df.loc[(df['currentnumber'] == 1), 'employs_several'] = 0

    logreg(df[['employs_several']] , x)

#demographics()

############################################################################################################################################### Section 5.4.6 (Propensity variance across educations).

df = df_Master[['propensity', 'edunum']]

stat, p = kruskal(*[group["propensity"].values for name, group in df.groupby("edunum")])
interpret_kruskal(stat, p)

