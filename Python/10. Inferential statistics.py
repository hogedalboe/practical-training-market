import config
import objects

db = objects.Database(config.server, config.database, config.user, config.password)

# Get query for obtaining master data.
masterQuery = ""
with open(r'C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\PostgreSQL\10. Master data query.sql', 'r') as f:
    masterQuery = f.read()

# Get all data of relevance for the descriptive statistical analysis.
df_Master = db.Read(masterQuery)

################################################################################################################################ 












################################################################################################################################ Test: Multiple linear regression

# https://datatofish.com/statsmodels-linear-regression/

import statsmodels.api as sm

# Does geographical variables influence the current amount of employed students?
df_Geography = df_Master[['currentamount', 'nearestfacilitykm', 'avgcommutekm']].dropna()

X = df_Geography[['nearestfacilitykm', 'avgcommutekm']]
Y = df_Geography['currentamount']
X = sm.add_constant(X)

model = sm.OLS(Y, X).fit()
print_model = model.summary()
print(print_model)