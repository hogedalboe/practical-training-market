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



















################################################################################################################################ Test: Multiple linear regression with scikit-learn

# https://stackabuse.com/linear-regression-in-python-with-scikit-learn/









################################################################################################################################ Test: Multiple linear regression with statsmodels

# https://datatofish.com/statsmodels-linear-regression/

import statsmodels.api as sm

# Does geographical variables influence the current amount of employed students?
df_Geography = df_Master[['currentamount', 'nearestfacilitykm', 'avgcommutekm']].dropna()
print("n = " + str(len(df_Geography.index)))
omitted = len(df_Master.index)-len(df_Geography.index)
print(str(omitted) + " observations were omitted due to missing values.")

X = df_Geography['avgcommutekm']
Y = df_Geography['nearestfacilitykm']

# Scatter plot.
import matplotlib.pyplot as plt
plt.scatter(X, Y)
plt.show()

#X = df_Geography[['nearestfacilitykm', 'avgcommutekm']]

# Add the intercept (https://stackoverflow.com/questions/20701484/why-do-i-get-only-one-parameter-from-a-statsmodels-ols-fit).
X = sm.add_constant(X)

model = sm.OLS(Y, X).fit()
print_model = model.summary()
print(print_model)
print("f-value: " + str(float(model.fvalue)))
