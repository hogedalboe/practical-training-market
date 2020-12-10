import psycopg2
import pandas
import numpy

import objects
import config

db = objects.Database(config.server, config.database, config.user, config.password)

# Read population data.
dfPopulation = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Population (2019).xlsx", skiprows=2,  nrows=106, usecols='D:E')

########################################################################################################################################################### Municipality population

# Get municipalities in database.
dfMunicipalities = db.Read("SELECT * FROM municipality")

# Insert each population number.
for i, row in dfMunicipalities.iterrows():

    # Identify corresponding population data.
    populationResult = "NULL"
    populationResults = dfPopulation[dfPopulation['Enhed'].str.contains(row['name'].replace('s Kommune','').replace(' Kommune',''))]
    if len(populationResults.index) == 1:
        populationResult = populationResults.iloc[0]['2019K4']

    sql = """UPDATE municipalitydemographics SET population = {0} WHERE municipalitycode = {1};""".format(populationResult, row['municipalitycode'])
    #db.Insert(sql)
#db.Commit()

########################################################################################################################################################### Region population

# Get regions in database.
dfRegions = db.Read("SELECT * FROM region")

# Insert each population number.
for i, row in dfRegions.iterrows():

    # Identify corresponding population data.
    populationResult = "NULL"
    populationResults = dfPopulation[dfPopulation['Enhed'].str.contains(row['name'].replace('Region ',''))]
    if len(populationResults.index) == 1:
        populationResult = populationResults.iloc[0]['2019K4']

    sql = """INSERT INTO regiondemographics(yearofmeasurement, regioncode, population) VALUES({0}, {1}, {2});""".format('2019', row['regioncode'], populationResult)
    db.Insert(sql)
db.Commit()

########################################################################################################################################################### Disconnect from database

db.Disconnect()