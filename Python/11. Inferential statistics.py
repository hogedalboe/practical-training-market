import config
import objects

import matplotlib.pyplot as plt
import seaborn as sns
import pandas
import numpy as np 
import scipy.stats
from scipy.stats import shapiro
import statsmodels.api as sm 

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

############################################################################################################################################### Section 5.4.2 (Company attributes and implications of missing data).

# https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.Logit.html
# https://www.geeksforgeeks.org/logistic-regression-using-statsmodels/

df = df_Master[['currentnumber', 'approvalnumber', 'propensity', 'netresult', 'established', 'employees']]

print(df.head(100))

# Creating dummy (dependent) variables.
df.loc[~df['employees'].isnull(), 'dummy_employees'] = 1
df.loc[df['employees'].isnull(), 'dummy_employees'] = 0

print(df.head(100))

# defining the dependent and independent variables 
x = df[['currentnumber', 'approvalnumber', 'propensity']] 
y = df[['dummy_employees']] 
   
# building the model and fitting the data 
log_reg = sm.Logit(y, x).fit() 

print(log_reg.summary())

# Fortolkning: Større sandsynlighed for at en pågældende virksomhed har data om antal ansatte, jo færre elever den har ansat...