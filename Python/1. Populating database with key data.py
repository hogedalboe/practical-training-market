import psycopg2
import pandas
import numpy
import datetime

import objects
import config

db = objects.Database(config.server, config.database, config.user, config.password)

################################################################################################################################ Schools 

def schools():
    # Reading excel table rows to dataframe.
    df = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Schools.xlsx")

    # Avoiding dublicates.
    insertedSchools = []

    #Iterating rows and inserting unique schools in the school table in the database.
    for index, row in df.iterrows():
        if not row['Nr'] in insertedSchools:
            print(row['Nr'], row['Skole'])
            insertedSchools.append(row['Nr'])
            sql = """INSERT INTO school(schoolnum, name) VALUES({0}, '{1}');""".format(row['Nr'], row['Skole'])
            db.Insert(sql)

    db.Commit()

################################################################################################################################ Committees and educations 

def committeesEducations():
    # Reading excel table rows to dataframe.
    df = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Committees (09.09.2019).xlsx")

    # Avoiding dublicates.
    insertedCommittees = []
    insertedEducations = []

    # Iterating rows and inserting unique committees/educations in the committee/education table in the database.
    for index, row in df.iterrows():

        # Limiting to committees within IU.
        if row['Paraply'] == "92 IU":

            # Inserting committees.
            if not str(row['FU-nr.'])+str(row['Fagligt udvalg']) in insertedCommittees:
                print(row['FU-nr.'], row['Fagligt udvalg'])
                insertedCommittees.append(str(row['FU-nr.'])+str(row['Fagligt udvalg']))
                sql = """INSERT INTO committee(committeecode, name) VALUES({0}, '{1}');""".format(row['FU-nr.'], row['Fagligt udvalg'])
                db.Insert(sql)
            
            # Inserting educations.
            if not row['Udd.'] in insertedEducations:
                print(row['Udd.'], row['Udd.betegnelse'], row['FU-nr.'])
                insertedCommittees.append(row['Udd.'])
                sql = """INSERT INTO education(edunum, name, committeecode) VALUES({0}, '{1}', {2});""".format(row['Udd.'], row['Udd.betegnelse'], row['FU-nr.'])
                db.Insert(sql)

    db.Commit()

################################################################################################################################ Subnational

def subnational():
    # Reading excel table rows to dataframe.
    df = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Subnational.xls")

    # Avoiding dublicates.
    insertedRegions = []
    insertedMunicipalities = []
    insertedPostalAreas = []

    # Iterating rows and inserting unique subnational data in the corresponding tables in the database.
    for index, row in df.iterrows():
        
        # Inserting regions.
        if not row['AMTS_NR'] in insertedRegions:
            print(row['AMTS_NR'], row['ADRESSERINGSNAVN'])
            insertedRegions.append(row['AMTS_NR'])
            sql = """INSERT INTO region(regioncode, name) VALUES({0}, '{1}');""".format(row['AMTS_NR'], row['ADRESSERINGSNAVN'])
            db.Insert(sql)

        # Inserting municipalities.
        if not row['KOMMUNE_NR'] in insertedMunicipalities:
            print(row['KOMMUNE_NR'], row['ADRESSERINGSNAVN_1'], row['AMTS_NR'])
            insertedMunicipalities.append(row['KOMMUNE_NR'])
            sql = """INSERT INTO municipality(municipalitycode, name, regioncode) VALUES({0}, '{1}', {2});""".format(row['KOMMUNE_NR'], row['ADRESSERINGSNAVN_1'], row['AMTS_NR'])
            db.Insert(sql)

        # Inserting postal areas.
        if not row['POSTNR'] in insertedPostalAreas:
            print(row['POSTNR'], row['KOMMUNE_NR'], row['BYNAVN'])
            insertedPostalAreas.append(row['POSTNR'])
            sql = """INSERT INTO postalarea(postalcode, municipalitycode, city) VALUES({0}, {1}, '{2}');""".format(row['POSTNR'], row['KOMMUNE_NR'], row['BYNAVN'])
            db.Insert(sql)

    db.Commit()

################################################################################################################################ Facilities

def facilities():
    # Reading excel table rows to dataframe.
    df = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Schools.xlsx")

    # Avoiding dublicates.
    insertedFacilities = []

    # Iterating rows and inserting unique facility data in the corresponding tables in the database.
    for index, row in df.iterrows():
        if not str(row['Nr'])+str(row['Udd']) in insertedFacilities:

            # Split the addresses into street/street number and postal area code/city segments.
            segments = row['Adresse'].split(',')

            # Parse streets and street numbers from the first address segment.
            street = ""
            streetNumber = 0
            streetElements = segments[0].split()
            for streetElement in streetElements:
                if not streetElement.isdigit():
                    street += streetElement+" "
                else:
                    streetNumber = int(streetElement)
            street = street.strip()

            # Parse postal area codes and city names from the second address segment.
            postal = 0
            city = ""
            postalElements = segments[1].split()
            for postalElement in postalElements:
                if not postalElement.isdigit():
                    city += postalElement+" "
                else:
                    postal = int(postalElement)
            city = city.strip()

            print(street, str(streetNumber), str(postal), city)

            insertedFacilities.append(str(row['Nr'])+str(row['Udd']))

            # Insert facilities.
            sql = """INSERT INTO facility(schoolnum, edunum, street, streetnumber, city, postalcode) VALUES({0}, {1}, '{2}', {3}, '{4}', {5});""".format(row['Nr'], row['Udd'], street, streetNumber, city, postal)
            db.Insert(sql)

    db.Commit()

################################################################################################################################ Specializations

def specializations():
    # Reading excel table rows to dataframe.
    df = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Approvals (05.09.2019).xlsx")

    # Avoiding dublicates.
    insertedSpecializations = []

    # Getting existing educations in database.
    dfEdu = db.Read("SELECT edunum FROM education")

    # Iterating rows and inserting unique specilizations in the specialization table in the database.
    for index, row in df.iterrows():
        if not str(row['CØSA-nr.'])+row['Spec.+Betegnelse'] in insertedSpecializations:

            # Split the specialization cells into specialization number and specialization name.
            spec = row['Spec.+Betegnelse'].split()
            specNum = int(spec[0])
            specName = row['Spec.+Betegnelse'].replace(spec[0]+" ", "")

            # Verify that the correponding education already exists in the database. Otherwise ignore the specialization.
            if not row['CØSA-nr.'] in dfEdu.values:
                print("Omitting education/specialization '{0}'/'{1}' because it does not exist in the database.".format(row['Udd.+Betegnelse'],row['Spec.+Betegnelse']))

            # Inserting specializations.
            else:
                print(str(row['CØSA-nr.']), str(specNum), specName)
                insertedSpecializations.append(str(row['CØSA-nr.'])+row['Spec.+Betegnelse'])
                sql = """INSERT INTO specialization(specnum, edunum, name) VALUES({0}, {1}, '{2}');""".format(specNum, row['CØSA-nr.'], specName)
                db.Insert(sql)

    db.Commit()

################################################################################################################################ Sectors

def sectors():
    # Reading excel table rows to dataframe.
    df = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Approvals (05.09.2019).xlsx")

    # Replacing all empty cells 'nan' with empty string values.
    df = df.replace(numpy.nan, "", regex=True)

    # Avoiding dublicates.
    insertedSectors = []

    # Iterating rows and inserting unique specilizations in the specialization table in the database.
    for index, row in df.iterrows():
        if str(row['Branchekode']) != "":
            if not str(row['Branchekode'])+row['Branchenavn'] in insertedSectors:

                # Removing characters causing insertion issues.
                brancheNavn = row['Branchenavn'].replace("'", "")

                print(str(row['Branchekode']), row['Branchenavn'])
                insertedSectors.append(str(row['Branchekode'])+row['Branchenavn'])
                sql = """INSERT INTO sector(sectorcode, sectorname) VALUES({0}, '{1}');""".format(row['Branchekode'], brancheNavn)
                db.Insert(sql)

    db.Commit()

################################################################################################################################ Businesses

def business():
    # Reading excel table rows to dataframe.
    df = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Approvals (05.09.2019).xlsx")

    # Replacing all empty cells 'nan' with empty string values.
    df = df.replace(numpy.nan, "", regex=True)

    # Avoiding dublicates.
    insertedBusiness = []

    # Iterating rows and inserting unique business types in the business type table in the database.
    for index, row in df.iterrows():
        if str(row['Selskabsform']) != "":
            if not row['Selskabsform'] in insertedBusiness:

                print(str(row['Selskabsform']), row['Selskabsform-tekst'])
                insertedBusiness.append(row['Selskabsform'])
                sql = """INSERT INTO business(businesscode, name) VALUES({0}, '{1}');""".format(row['Selskabsform'], row['Selskabsform-tekst'])
                db.Insert(sql)

    db.Commit()

################################################################################################################################ Companies

def company():
    # Reading excel table rows to dataframe.
    df = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Approvals (05.09.2019).xlsx")

    # Replacing all empty cells 'nan' with empty string values.
    df = df.replace(numpy.nan, "", regex=True)

    # Avoiding dublicates.
    insertedCompany = []

    # Iterating rows and inserting unique companies in the company table in the database.
    for index, row in df.iterrows():
        if str(row['CVR-nr.']) != "":
            if not row['CVR-nr.'] in insertedCompany:
                if type(row['CVR-nr.']) == int:

                    # Removing characters causing insertion issues.
                    name = row['Navn'].replace("'", "")

                    # Formatting NULL values.
                    sector = row['Branchekode']
                    business = row['Selskabsform']
                    website = row['Internetadresse']
                    if name == "":
                        name = "NULL"
                    if sector == "":
                        sector = "NULL"
                    if business == "":
                        business = "NULL"
                    if website == "":
                        website = "NULL"
                    
                    print(row['CVR-nr.'], name)
                    insertedCompany.append(row['CVR-nr.'])
                    sql = """INSERT INTO company(cvrnum, name, sectorcode, businesscode, website) VALUES({0}, '{1}', {2}, {3}, '{4}');""".format(row['CVR-nr.'], name, sector, business, website)
                    db.Insert(sql)

    db.Commit()

################################################################################################################################ Production units

def productionUnits():
    # Reading excel table rows to dataframe.
    df = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Approvals (05.09.2019).xlsx")

    # Replacing all empty cells 'nan' with empty string values.
    df = df.replace(numpy.nan, "", regex=True)

    # Avoiding dublicates.
    insertedProductionUnit = []
    
    # Iterating rows and inserting unique production units in the productionunit table in the database.
    for index, row in df.iterrows():
        if str(row['P-nr']) != "":
            if not row['P-nr'] in insertedProductionUnit:
                if not type(row['P-nr']) == int:
                    if row['P-nr'] != 0:

                        # Removing characters causing insertion issues.
                        adresse = row['Adresse'].replace("'", "")

                        # Parse streets and street numbers from the first address segment.
                        street = ""
                        streetNumber = 0
                        streetElements = adresse.split()
                        for streetElement in streetElements:
                            if not streetElement.isdigit():
                                street += streetElement+" "
                            else:
                                streetNumber = int(streetElement)
                        street = street.strip()

                        # Parse postal area codes and city names from the second address segment.
                        postal = 0
                        city = ""
                        postalElements = row['Postnr.+Distrikt'].split()
                        for postalElement in postalElements:
                            if not postalElement.isdigit():
                                city += postalElement+" "
                            else:
                                postal = int(postalElement)
                        city = city.strip()

                        print(row['P-nr'], row['CVR-nr.'], street, str(streetNumber), city, str(postal))
                        insertedProductionUnit.append(row['P-nr'])
                        sql = """INSERT INTO productionunit(pnum, cvrnum, street, streetnumber, city, postalcode) VALUES({0}, {1}, '{2}', {3}, '{4}', {5});""".format(row['P-nr'], row['CVR-nr.'], street, streetNumber, city, postal)
                        db.Insert(sql)

    db.Commit()

################################################################################################################################ Limitations

def limitations():
    # Reading excel table rows to dataframe.
    df = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Approvals (05.09.2019).xlsx")

    # Replacing all empty cells 'nan' with empty string values.
    df = df.replace(numpy.nan, "", regex=True)

    # Avoiding dublicates.
    insertedLimitations = []

    # Iterating rows and inserting unique limitations in the limitation table in the database.
    def insertLimitations(columnName):
        for index, row in df.iterrows():
            if row[columnName] != "":
                if row[columnName] != " ":
                    if not row[columnName] in insertedLimitations:

                        # Parsing limitation cell value.
                        limitationCode = int(row[columnName].split()[0])
                        limitationName = row[columnName].replace(str(limitationCode)+" ", "")

                        print(str(limitationCode), limitationName)
                        insertedLimitations.append(row[columnName])
                        sql = """INSERT INTO limitation(limitationcode, name) VALUES({0}, '{1}');""".format(limitationCode, limitationName)
                        db.Insert(sql)


    insertLimitations("Begrænsning 1")
    insertLimitations("Begrænsning 2")

    db.Commit()

################################################################################################################################ Approvals

def approvals():
    # Reading excel table rows to dataframe.
    df = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Approvals (05.09.2019).xlsx")

    # Replacing all empty cells 'nan' with empty string values.
    df = df.replace(numpy.nan, "", regex=True)

    # Avoiding dublicates.
    insertedApprovals = []

    # Getting existing production units in database.
    dfProductionUnits = db.Read("SELECT pnum FROM productionunit")

    # Commiting only a bulk insertion at a time.
    count = 0
    bulk = 1000

    # Iterating rows and inserting approvals in the approval table in the database.
    for index, row in df.iterrows():
        if row['P-nr'] != "":
            if int(row['P-nr']) in dfProductionUnits.values:
                    if not str(row['P-nr'])+str(row['CØSA-nr.'])+row['Spec.+Betegnelse'] in insertedApprovals:
                        if row['CØSA-nr.'] != 1290:

                            # Parse specialization number.
                            specNum = int(row['Spec.+Betegnelse'].split()[0])

                            # Handling NULL values.
                            approvalAmount = 0
                            if not row['Godk. antal'] == "":
                                approvalAmount = row['Godk. antal']

                            currentamount = 0
                            if not row['Antal igangv. aft'] == "":
                                currentamount = row['Antal igangv. aft']

                            otherActive = 0
                            if not row['Antal igangv. øvr. aft.'] == "":
                                otherActive = row['Antal igangv. øvr. aft.']

                            print(str(specNum), str(row['CØSA-nr.']), str(row['P-nr']), str(row['Godk.dato']), str(row['Godk. antal']), str(row['Antal igangv. aft']), str(row['Antal igangv. øvr. aft.']))
                            insertedApprovals.append(str(row['P-nr'])+str(row['CØSA-nr.'])+row['Spec.+Betegnelse'])
                            sql = """INSERT INTO approval(specnum, edunum, pnum, approvaldate, approvalamount, currentamount, otheractive) VALUES({0}, {1}, {2}, '{3}', {4}, {5}, {6});""".format(specNum, row['CØSA-nr.'], row['P-nr'], row['Godk.dato'], approvalAmount, currentamount, otherActive)
                            db.Insert(sql)

                            count += 1

                            if count >= bulk:
                                db.Commit()
                                count = 0

    db.Commit()

################################################################################################################################ Limititation relationships

def limits():
    # Reading excel table rows to dataframe.
    df = pandas.read_excel(r"C:\Users\hoged\OneDrive\Skrivebord\Speciale\Data\Approvals (05.09.2019).xlsx")

    # Replacing all empty cells 'nan' with empty string values.
    df = df.replace(numpy.nan, "", regex=True)

    # Avoiding dublicates.
    insertedLimits = []

    # Getting existing production units in database.
    dfProductionUnits = db.Read("SELECT pnum FROM productionunit")

    # Iterating rows and inserting unique limitations in the limitation table in the database.
    def insertLimits(columnName):

        # Commiting only a bulk insertion at a time.
        count = 0
        bulk = 1000

        for index, row in df.iterrows():
            if row[columnName] != "":
                if row[columnName] != " ":
                    if row['P-nr'] != "":
                        if int(row['P-nr']) in dfProductionUnits.values:
                            if row['CØSA-nr.'] != 1290:
                                if not row[columnName]+str(row['Spec.+Betegnelse'])+str(row['CØSA-nr.'])+str(row['P-nr']) in insertedLimits:

                                    # Parsing limitation cell value.
                                    limitationCode = int(row[columnName].split()[0])

                                    # Parse specialization number.
                                    specNum = int(row['Spec.+Betegnelse'].split()[0])

                                    print(row[columnName]+str(row['Spec.+Betegnelse'])+str(row['CØSA-nr.'])+str(row['P-nr']))
                                    insertedLimits.append(row[columnName]+str(row['Spec.+Betegnelse'])+str(row['CØSA-nr.'])+str(row['P-nr']))
                                    sql = """INSERT INTO limits(limitationcode, specnum, edunum, pnum) VALUES({0}, {1}, {2}, {3});""".format(limitationCode, specNum, row['CØSA-nr.'], row['P-nr'])
                                    db.Insert(sql)

                                    count += 1

                                    if count >= bulk:
                                        db.Commit()
                                        count = 0

        db.Commit()

    insertLimits("Begrænsning 1")
    insertLimits("Begrænsning 2")

################################################################################################################################ Execute the population functions

#schools()
#committeesEducations()
#subnational()
#facilities()
#specializations()
#sectors()
#business()
#company()
#productionUnits()
#limitations()
#approvals()
#limits()

################################################################################################################################ Disconnect database

db.Disconnect()