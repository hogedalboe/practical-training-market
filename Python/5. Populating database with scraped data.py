import psycopg2
import pandas
import numpy
import datetime

import objects
import config

db = objects.Database(config.server, config.database, config.user, config.password)

# Get file lines.
def getFileLines(file):
    lines = []
    with open(file, 'r+') as f:
        lines = f.readlines()
    return lines

# Chunk size limit of the database (no more than 1000 observation should be inserted at once).
chunkLimit = 500

################################################################################################################ Krak routing data

def insertRoutingData():
    count = 0

    # Duplicate key control.
    dbKeys = []
    duplicates = []

    # Read the routing data line by line.
    distances = getFileLines(config.file_distances)
    for i, distance in enumerate(distances):

        if i > 0:
            routeElements = distance.split(";")

            # Route must have six elements to be valid.
            if len(routeElements) == 6:

                postalcode = routeElements[0]
                facilityid = routeElements[2]

                # Avoid duplicate keys.
                if not str(postalcode)+str(facilityid) in dbKeys:

                    # Insert route in database.
                    sql = """INSERT INTO distance(postalcode, facilityid, km, hours, minutes) VALUES({0}, {1}, {2}, {3}, {4});""".format(
                        postalcode,
                        facilityid,
                        routeElements[3],
                        routeElements[4],
                        routeElements[5]
                    )
                    db.Insert(sql)

                    # Avoid duplicate keys.
                    dbKeys.append(str(postalcode)+str(facilityid))

                    # Manage insertion chunk sizes.
                    count += 1

                else:
                    duplicates.append(distance)
                    print("Key value (postalcode, facilityid)=({0},{1}) violates unique constraint and was not inserted.".format(postalcode,facilityid))

            else:
                print("Omitted route '{0}' due to missing data in the observation.".format(distance))
        
        if count > chunkLimit:
            db.Commit()
            count = 0

    db.Commit()

    if len(duplicates) > 0:
        print("The following {0} observations are duplicates and were not inserted into the database:".format(str(len(duplicates))))
        for duplicate in duplicates:
            print("\t\t" + duplicate)

#insertRoutingData()

################################################################################################################ Proff financial data

def insertFinancialData():
    count = 0

    # Duplicate key control.
    dbKeys = []
    duplicates = []

    # Read the financial data line by line.
    financials = getFileLines(config.file_financials)
    for i, financial in enumerate(financials):

        if i > 0:
            financialElements = financial.split(";")

            # Financial data must have six elements to be valid.
            if len(financialElements) == 13:

                cvrnum = financialElements[0]
                pubyear = financialElements[3]

                liquidityratio = financialElements[4].replace(".","").replace(",",".")
                if liquidityratio == "-":
                    liquidityratio = "NULL"

                roi = financialElements[5].replace(".","").replace(",",".")
                if roi == "-":
                    roi = "NULL"

                solvencyratio = financialElements[6].replace(".","").replace(",",".")
                if solvencyratio == "-":
                    solvencyratio = "NULL"

                netturnover = financialElements[7].replace(".","").replace(",",".")
                if netturnover == "-":
                    netturnover = "NULL"

                grossprofit = financialElements[8].replace(".","").replace(",",".")
                if grossprofit == "-":
                    grossprofit = "NULL"

                equity = financialElements[9].replace(".","").replace(",",".")
                if equity == "-":
                    equity = "NULL"

                netresult = financialElements[10].replace(".","").replace(",",".")
                if netresult == "-":
                    netresult = "NULL"

                currency = financialElements[11]

                # Avoid duplicate keys.
                if not str(cvrnum)+str(pubyear) in dbKeys:

                    # Insert route in database.
                    sql = """INSERT INTO financial(cvrnum, pubyear, liquidityratio, roi, solvencyratio, netturnover, grossprofit, equity, netresult, currency) VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9});""".format(
                        cvrnum,
                        pubyear,
                        liquidityratio,
                        roi,
                        solvencyratio,
                        netturnover,
                        grossprofit,
                        equity,
                        netresult,
                        currency
                    )
                    db.Insert(sql)

                    # Avoid duplicate keys.
                    dbKeys.append(str(cvrnum)+str(pubyear))

                    # Manage insertion chunk sizes.
                    count += 1

                else:
                    duplicates.append(financial)
                    print("Key value (cvrnum, pubyear)=({0},{1}) violates unique constraint and was not inserted.".format(cvrnum,pubyear))

            else:
                print("Omitted financial data '{0}' due to missing data in the observation.".format(financial))
        
        if count > chunkLimit:
            db.Commit()
            count = 0

    db.Commit()

    if len(duplicates) > 0:
        print("The following {0} observations are duplicates and were not inserted into the database:".format(str(len(duplicates))))
        for duplicate in duplicates:
            print("\t\t" + duplicate)

insertFinancialData()




