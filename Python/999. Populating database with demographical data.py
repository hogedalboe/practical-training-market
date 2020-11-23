import psycopg2
import pandas
import numpy
import datetime

import objects
import config

db = objects.Database(config.server, config.database, config.user, config.password)

# Dataframe columns to store prepared data (and to query database).
yearofmeasurement = "yearofmeasurement"
municipalitycode = "municipalitycode"
avgcommutekm = "avgcommutekm"
employmentrate = "employmentrate"
employmentavailabilityrate = "employmentavailabilityrate"
yearlydisposableincome = "yearlydisposableincome"

# Get municipalities in database.
dfMunicipalities = db.Read("SELECT * FROM municipality")

# Read income data.
dfIncome = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Income (2018).xlsx", skiprows=2,  nrows=98, usecols='D:E')

# Read commuting data.
dfCommute = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Commute (2018).xlsx", skiprows=2,  nrows=99, usecols='C:D')

# Read employment data.
dfEmployment = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Employment (2018).xlsx", skiprows=2,  nrows=99, usecols='E:G')

data = {
    yearofmeasurement:[],
    municipalitycode:[],
    avgcommutekm:[],
    employmentrate:[],
    employmentavailabilityrate:[],
    yearlydisposableincome:[]
}

# Iterate municipalities to append demographical data.
for i, row in dfMunicipalities.iterrows():

    # Identify corresponding commute data.
    commuteResult = "NULL"
    commuteResults = dfCommute[dfCommute['Kommune'].str.contains(row['name'].replace('s Kommune','').replace(' Kommune',''))]
    if len(commuteResults.index) == 1:
        commuteResult = commuteResults.iloc[0]['2018']

    # Identify corresponding employment data.
    employmentrateResult = "NULL"
    employmentavailabilityrateResult = "NULL"
    employmentResults = dfEmployment[dfEmployment['Kommune'].str.contains(row['name'].replace('s Kommune','').replace(' Kommune',''))]
    if len(employmentResults.index) == 1:
        employmentrateResult = employmentResults.iloc[0]['Beskæftigelsesfrekvens']
        employmentavailabilityrateResult = employmentResults.iloc[0]['Erhvervsfrekvens']

    # Identify corresponding income data.
    incomeResult = "NULL"
    incomeResults = dfIncome[dfIncome['Kommune'].str.contains(row['name'].replace('s Kommune','').replace(' Kommune',''))]
    if len(incomeResults.index) == 1:
        incomeResult = incomeResults.iloc[0]['2018']

    # Append identified demographics for the municipality to dictionary.
    data[yearofmeasurement].append(2018)
    data[municipalitycode].append(row['municipalitycode'])
    data[avgcommutekm].append(commuteResult)
    data[employmentrate].append(employmentrateResult)
    data[employmentavailabilityrate].append(employmentavailabilityrateResult)
    data[yearlydisposableincome].append(incomeResult)

# Create dataframe to insert into database.
dfDemographics = pandas.DataFrame(data, columns=[yearofmeasurement,municipalitycode,avgcommutekm,employmentrate,employmentavailabilityrate,yearlydisposableincome])

# Write dataframe to database.
for i, row in dfDemographics.iterrows():
    sql = """INSERT INTO municipalitydemographics({0}, {1}, {2}, {3}, {4}, {5}) VALUES({6}, {7}, {8}, {9}, {10}, {11});""".format(
        yearofmeasurement,
        municipalitycode,
        avgcommutekm,
        employmentrate,
        employmentavailabilityrate,
        yearlydisposableincome,
        row[yearofmeasurement],
        row[municipalitycode],
        row[avgcommutekm],
        row[employmentrate],
        row[employmentavailabilityrate],
        row[yearlydisposableincome]
    )
    db.Insert(sql)

db.Commit()

db.Disconnect()